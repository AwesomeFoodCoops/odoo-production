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
    shift_state_delay_duration = fields.Integer(
        "Alert State Duration",
        required=True,
    )

    # Constraints

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
    @api.constrains('shift_state_delay_duration')
    def _check_shift_state_delay_duration(self):
        for res in self:
            if res.shift_state_delay_duration <= 0:
                raise ValidationError(_(
                    "Alert State Duration has to be bigger than 0."))

    # Read / Write

    @api.multi
    def set_shift_weeks_per_cycle(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'coop_shift.number_of_weeks_per_cycle', self.shift_weeks_per_cycle)

    @api.multi
    def set_shift_shift_week_a_date(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'coop_shift.week_a_date', self.shift_week_a_date)

    @api.multi
    def set_shift_state_delay_duration(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'coop.shift.state.delay.duration', self.shift_state_delay_duration)

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
    def get_default_shift_state_delay_duration(self):
        return {
            'shift_state_delay_duration':
                int(self.env['ir.config_parameter'].sudo().get_param(
                    'coop.shift.state.delay.duration'))
        }

    # Actions

    @api.multi
    def action_recompute_shift_weeks(self):
        self.ensure_one()
        self.execute()
        # do recompute
        self._recompute_week_number(
            'shift_template', 'start_date', 'week_number', 'week_name')
        self._recompute_week_number(
            'shift_shift', 'date_without_time', 'week_number', 'week_name')
        # recompute name, should also trigger the update on shifts
        # because it's related
        _logger.info('Recomputing shifts names..')
        self.with_context(
            active_check=False,
        ).env['shift.template'].search([])._compute_template_name()

    @api.model
    def _recompute_week_number(
        self, table, field_date, field_week_number, field_week_name=None
    ):
        """
            Updates week_number and week_name using SQL.
            Beware that, even though this is blazing fast, it bypasses the ORM.
            So computed fields that depend on these fields,
            will not be recomputed.

            In any case, we prefer performance here.
            All recomputations should be managed manually by overloading this
            method.
        """
        _logger.info(
            'Recomputing week_number and week_name for table %s', table)
        # Update week_number
        get_param = self.env['ir.config_parameter'].sudo().get_param
        weekA_date = get_param('coop_shift.week_a_date')
        n_weeks_cycle = int(get_param('coop_shift.number_of_weeks_per_cycle'))

        self.env.cr.execute("""
            UPDATE {table}
            SET {field_week_number} = (
                1 +
                MOD(DIV(ABS({field_date}::date - %s::date)::integer, 7), %s)
            )::integer
            WHERE {field_date} IS NOT NULL
        """.format(
            table=table,
            field_date=field_date,
            field_week_number=field_week_number,
        ), (weekA_date, n_weeks_cycle))
        # Update week_name
        if field_week_name:
            self.env.cr.execute("""
                UPDATE {table}
                SET {field_week_name} = CHR(64 + {field_week_number})
                WHERE {field_week_number} IS NOT NULL
            """.format(
                table=table,
                field_week_name=field_week_name,
                field_week_number=field_week_number,
            ))
