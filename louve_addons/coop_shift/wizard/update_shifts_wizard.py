# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
# from datetime import datetime, timedelta
# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
# from openerp.exceptions import UserError


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
            if (not date_from or shift.date_begin >= date_from) and\
                    (not date_to or shift.date_end <= date_to) and\
                    shift.state == "draft":
                line_ids.append((0, 0, {
                    'wizard_id': self.id,
                    'shift_id': shift,
                    'name': shift.name,
                    'user_id': shift.user_id.id,
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
            wizard.line_ids = self._get_line_ids(
                wizard.template_id, date_from=wizard.date_from,
                date_to=wizard.date_to)

    @api.multi
    def update_shifts(self):
        shift_obj = self.env["shift.shift"]
        for wizard in self:
            if self.updated_fields and\
                    isinstance(eval(self.updated_fields), dict):
                vals = eval(self.updated_fields)
                if "updated_fields" in vals.keys():
                    vals = eval(vals["updated_fields"])
                shift_ids = [line.shift_id.id for line in wizard.line_ids]
                shift_obj.browse(shift_ids).with_context(
                    tracking_disable=True).write(vals)
                wizard.template_id.updated_fields = ""
        return True

    # @api.multi
    # def write(self, vals):
    #     import pdb; pdb.set_trace()
    #     if vals.get("updated_fields", False) and\
    #             "updated_fields" in vals["updated_fields"]:
    #         del vals['updated_fields']
    #     return super(UpdateShiftsWizard, self).write(vals)


class UpdateShiftsWizardLine(models.TransientModel):
    _name = 'update.shifts.wizard.line'
    _description = 'Update Shifts Wizard Line'

    wizard_id = fields.Many2one(
        'update.shifts.wizard', 'Wizard Reference', required=True)
    shift_id = fields.Many2one(
        'shift.shift', 'Shift Reference', required=True)
    name = fields.Char('Name')
    user_id = fields.Many2one('res.partner', string='Responsible')
    shift_type_id = fields.Many2one('shift.type', string='Category')
    date_begin = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='Start Date')
    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'), ('done', 'Done')],
        string='Status')
