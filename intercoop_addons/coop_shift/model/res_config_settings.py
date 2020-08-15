# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'coop_shift.config.settings'

    shift_weeks_per_cycle = fields.Integer(
        'Number of Weeks per Cycle',
        required=True,
    )
    shift_week_a_date = fields.Date(
        'Week A start date',
        required=True,
    )

    @api.multi
    @api.constrains('shift_weeks_per_cycle')
    def _check_shift_weeks_per_cycle(self):
        for res in self:
            if res.shift_weeks_per_cycle <= 0:
                raise ValidationError(_(
                    "Number of Weeks per Cycle has to be bigger than 0."))

    @api.multi
    @api.constrains('shift_week_a_date')
    def _check_shift_week_a_date(self):
        for rec in self:
            if rec.shift_week_a_date > fields.Date.today():
                raise ValidationError(_(
                    "The Week A start date can't be a future date."))

    @api.multi
    def set_shift_weeks_per_cycle(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'coop_shift.number_of_weeks_per_cycle', self.shift_weeks_per_cycle)

    @api.multi
    def set_shift_shift_week_a_date(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'coop_shift.week_a_date', self.shift_week_a_date)

    @api.multi
    def get_default_shift_weeks_per_cycle(self):
        return {
            'shift_weeks_per_cycle':
                int(self.env['ir.config_parameter'].sudo().get_param(
                    'coop_shift.number_of_weeks_per_cycle'))
        }

    @api.multi
    def get_default_shift_week_a_date(self):
        return {
            'shift_week_a_date':
                self.env['ir.config_parameter'].sudo().get_param(
                    'coop_shift.week_a_date')
        }

    @api.multi
    def action_recompute_shift_weeks(self):
        self.ensure_one()
        self.execute()
        # do recompute
        _logger.info("Creating jobs to recompute week_name in shift.template.")
        self.env['shift.template'].with_context(
            active_test=False
        ).search([])._recompute_week_number_async()
        _logger.info("Creating jobs to recompute week_name in shift.shift..")
        self.env['shift.shift'].with_context(
            active_test=False
        ).search([])._recompute_week_number_async()
        # return alert
        return {
            'warning': {
                'title': _('In progress'),
                'message': _(
                    'They will be recomputed in the backend.\n'
                    'It may take several minutes to finish, you can view the '
                    'progress by checking the active queue jobs in '
                    'Conector > Jobs.'
                ),
            }
        }
