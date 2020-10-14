# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class UpdateShiftsWizard(models.TransientModel):
    _name = 'update.shifts.wizard'
    _description = 'Update Shifts Wizard'

    @api.model
    def _get_template_id(self):
        return self.env.context.get('active_id', False)

    @api.model
    def _get_line_ids(self, template, date_from=None, date_to=None):
        if not template:
            return None
        line_ids = []
        for shift in template.shift_ids:
            if (not date_from or shift.date_begin.date() >= date_from) and\
                    (not date_to or shift.date_end.date() <= date_to) and\
                    shift.state == "draft":
                line_ids.append((0, 0, {
                    'wizard_id': self.id,
                    'shift_id': shift,
                    'name': shift.name,
                    'user_ids': [(6, 0, shift.user_ids.ids)],
                    'shift_type_id': shift.shift_type_id.id,
                    'date_begin': shift.date_begin,
                    'date_end': shift.date_end,
                    'state': shift.state,
                }))
        return line_ids

    @api.model
    def _default_line_ids(self):
        template_id = self.env.context.get('active_id', False)
        if template_id:
            template = self.env['shift.template'].browse(template_id)
            return self._get_line_ids(
                template, date_from=self.date_from, date_to=self.date_to)

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        template_id = self.env.context.get('active_id', False)
        if template_id:
            template = self.env['shift.template'].browse(template_id)
            self.line_ids = [(5, 0, 0)]
            self.line_ids = self._get_line_ids(
                template, date_from=self.date_from, date_to=self.date_to)

    template_id = fields.Many2one('shift.template', default=_get_template_id)
    line_ids = fields.One2many(
        'update.shifts.wizard.line', 'wizard_id', default=_default_line_ids)
    date_from = fields.Date('Update shifts from')
    date_to = fields.Date('Update shifts until')
    updated_fields = fields.Char(
        related='template_id.updated_fields',
        string="""Changes to repercute on selected shifts""")

    @api.multi
    def update_lines(self, date_from=None, date_to=None):
        for wizard in self:
            wizard.line_ids = [(5, 0, 0)]
            wizard.line_ids = self._get_line_ids(
                wizard.template_id, date_from=wizard.date_from,
                date_to=wizard.date_to)

    @api.multi
    def update_shifts(self):
        shift_obj = self.env["shift.shift"]
        for wizard in self:
            if self.updated_fields and\
                    isinstance(safe_eval(self.updated_fields), dict):
                vals = safe_eval(self.updated_fields)
                if "updated_fields" in vals.keys():
                    vals = safe_eval(vals["updated_fields"])
                shift_ids = [line.shift_id.id for line in wizard.line_ids]
                special = []
                if 'shift_ticket_ids' in vals.keys():
                    special = ['shift_ticket_ids']
                    del vals['shift_ticket_ids']
                shift_obj.browse(shift_ids).with_context(
                    tracking_disable=True, special=special).write(vals)
                wizard.template_id.updated_fields = ""
        return True


class UpdateShiftsWizardLine(models.TransientModel):
    _name = 'update.shifts.wizard.line'
    _description = 'Update Shifts Wizard Line'

    wizard_id = fields.Many2one(
        'update.shifts.wizard',
        'Wizard Reference',
        required=True,
        ondelete="cascade",
    )
    shift_id = fields.Many2one(
        'shift.shift',
        'Shift Reference',
        required=True,
        ondelete="cascade",
    )
    name = fields.Char('Name')
    user_ids = fields.Many2many(
        'res.partner',
        string='Shift Leader',
        ondelete="set null",
    )
    shift_type_id = fields.Many2one(
        'shift.type',
        string='Category',
        ondelete="cascade",
    )
    date_begin = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='End Date')
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ],
        string='Status',
    )
