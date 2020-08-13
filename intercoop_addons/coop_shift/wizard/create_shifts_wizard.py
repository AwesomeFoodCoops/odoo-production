# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class CreateShifts(models.TransientModel):
    _name = 'create.shifts.wizard'
    _description = 'Create Shifts Wizard'

    @api.model
    def default_get(self, fields):
        res = super(CreateShifts, self).default_get(fields)
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
                    min(templates.mapped('start_datetime'))[0:10])
            else:
                # The first start date
                res['date_from'] = min(
                    templates.mapped('start_datetime'))[0:10]
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
            if wizard.date_from <= wizard.last_shift_date:
                raise ValidationError(_(
                    "'From date' can't be before 'Last shift date'"))
            for template in wizard.template_ids:
                template.create_shifts_from_template(
                    after=self.date_from, before=self.date_to)
