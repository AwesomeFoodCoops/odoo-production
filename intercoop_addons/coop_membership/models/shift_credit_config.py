# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class ShiftCreditConfig(models.Model):
    _name = 'shift.credit.config'

    credited_make_ups = fields.Selection(
        selection=[
            ('0.5', '0.5'),
            ('1.5', '1.5'),
            ('2', '2')
        ],
        required=True,
        string='Credited make-ups'
    )
    template_ids = fields.Many2many(
        comodel_name='shift.template',
        domain=[('active', '=', True)],
        required=True,
        string='Créneau'
    )
    end_date = fields.Date(
        string="Date de clôture de l’exception"
    )

    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('cancel', 'Canceled'),
        ],
        default='active'
    )

    apply_for_abcd = fields.Boolean(string="ABCD rattrapages")
    apply_for_volants = fields.Boolean(string="Volants")

    @api.multi
    @api.constrains('template_ids',
                    'state',
                    'end_date',
                    'apply_for_abcd',
                    'apply_for_volants')
    def _constraint_duplicated_templates(self):
        for config in self:
            duplicated_credit_configs = self.search([
                '&',
                '|',
                ('end_date', '=', False),
                ('end_date', '>', fields.Date.today()),
                '|',
                ('apply_for_abcd', '=', config.apply_for_abcd),
                ('apply_for_volants', '=', config.apply_for_volants),
                '&',
                ('template_ids', 'in', config.template_ids.ids),
                '&',
                ('state', '=', 'active'),
                ('id', '!=', config.id)
            ])
            if duplicated_credit_configs:
                raise ValidationError(_('The configuration is duplicated'))

    @api.multi
    def cancel(self):
        return self.write({
            'state': 'cancel'
        })
