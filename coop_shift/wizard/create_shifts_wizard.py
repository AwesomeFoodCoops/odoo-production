# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CreateShifts(models.TransientModel):
    _name = 'create.shifts.wizard'
    _description = 'Create Shifts Wizard'

    @api.model
    def _get_last_shift_date(self):
        if self.template_ids:
            return min([t.last_shift_date for t in self.template_ids])
        elif self.env.context.get('active_ids', False):
            return min([t.last_shift_date
                        for t in self.env['shift.template'].browse(
                            self.env.context['active_ids'])])
        else:
            return False

    @api.model
    def _get_default_date(self):
        lsd = self.last_shift_date or self._get_last_shift_date()
        if lsd:
            return lsd + timedelta(days=1)
        elif self.template_ids:
            return min([t.start_date for t in self.template_ids])
        else:
            return fields.Date.today()  # datetime.now()

    @api.model
    def _get_selected_templates(self):
        template_ids = self.env.context.get('active_ids', False)
        if template_ids:
            return template_ids
        template_id = self.env.context.get('active_id', False)
        if template_id:
            return template_id
        return []

    template_ids = fields.Many2many(
        'shift.template', 'template_createshift_rel', 'template_id',
        'wizard_id', string="Templates", default=_get_selected_templates)
    last_shift_date = fields.Date(
        'Last created shift date',
        default=_get_last_shift_date)
    date_from = fields.Date(
        'Plan this Template from',
        default=_get_default_date)
    date_to = fields.Date('Plan this Template until')

    @api.multi
    def create_shifts(self):
        for wizard in self:
            if wizard.last_shift_date and \
               wizard.date_from <= wizard.last_shift_date:
                raise ValidationError(_(
                    "'From date' can't be before 'Last shift date'"))
            for template in wizard.template_ids:
                template.create_shifts_from_template(
                    after=self.date_from, before=self.date_to)
