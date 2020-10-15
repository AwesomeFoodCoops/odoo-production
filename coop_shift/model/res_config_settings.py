# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    shift_weeks_per_cycle = fields.Integer(
        'Number of Weeks per Cycle',
        required=True,
        config_parameter="coop_shift.number_of_weeks_per_cycle",
    )
    shift_week_a_date = fields.Date(
        'Week A start date',
        required=True,
    )
    shift_state_delay_duration = fields.Integer(
        "Alert State Duration",
        required=True,
        config_parameter="coop.shift.state.delay.duration",
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

    @api.model
    def get_values(self):
        res = super().get_values()
        get_param = self.env["ir.config_parameter"].sudo().get_param
        shift_week_a_date = get_param("coop_shift.week_a_date", False)
        if shift_week_a_date:
            shift_week_a_date = fields.Date.from_string(shift_week_a_date)
        res.update(shift_week_a_date=shift_week_a_date)
        return res

    def set_values(self):
        super().set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        if self.shift_week_a_date:
            shift_week_a_date = fields.Date.to_string(self.shift_week_a_date)
            set_param("coop_shift.week_a_date", shift_week_a_date)

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
