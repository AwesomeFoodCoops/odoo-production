# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CreateShifts(models.TransientModel):
    _name = 'create.shifts.wizard'
    _description = 'Create Shifts Wizard'

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        # Get selected template_ids
        template_ids = []
        if self.env.context.get('active_ids'):
            template_ids = self.env.context.get('active_ids')
        elif self.env.context.get('active_id'):
            template_ids = [self.env.context.get('active_id')]
        res['template_ids'] = template_ids
        templates = self.env['shift.template'].browse(template_ids)
        # Get last shift date
        if templates:
            res['last_shift_date'] = min(templates.mapped('last_shift_date'))
        # Default start date
        if templates:
            if res.get('last_shift_date'):
                # Either the last shift date, or the first start date
                res['date_from'] = max(
                    res['last_shift_date'],
                    min(templates.mapped('start_datetime')).date(),
                )
            else:
                # The first start date
                res['date_from'] = \
                    min(templates.mapped('start_datetime')).date()
        else:
            res['date_from'] = fields.Date.today()
        return res

    template_ids = fields.Many2many('shift.template', string="Templates")
    last_shift_date = fields.Date('Last created shift date')
    date_from = fields.Date('Plan this Template from')
    date_to = fields.Date('Plan this Template until')

    @api.multi
    def create_shifts(self):
        for wizard in self:
            if (
                wizard.last_shift_date
                and wizard.date_from < wizard.last_shift_date
            ):
                raise ValidationError(_(
                    "'From date' can't be before 'Last shift date'"))
            for template in wizard.template_ids:
                template.create_shifts_from_template(
                    after=self.date_from, before=self.date_to)
