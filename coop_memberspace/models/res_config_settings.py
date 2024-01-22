# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    shift_exchange_duration = fields.Integer(
        string="Shift exchange duration (hour)",
        required=True,
        config_parameter="coop.shift.shift_exchange_duration",
        default=24
    )
    shift_replacement_duration = fields.Integer(
        string="Shift replacement duration (day)",
        required=True,
        config_parameter="coop.shift.shift_replacement_duration",
        default=90
    )
    shift_exchange_policy = fields.Selection([
        ('registraion', 'Participations put into exchange'),
        ('registraion_standard', 'Participations put into exchange plus available standard seats'),
        ('registraion_standard_ftop',
            'Participations put into exchange plus available standard seats plus available ftop seats'),
        ],
        string="Shift replacement list contains",
        required=True,
        config_parameter="coop.shift.shift_exchange_policy",
        default='registraion'
    )
    force_message_route = fields.Boolean(
        string="Force Message Route",
        config_parameter="coop_memberspace.force.message_route",
        default=False
    )
    ftop_shift_cancellation_duration = fields.Integer(
        string="FTOP shift cancellation duration (hour)",
        config_parameter="coop_memberspace.ftop_shift_cancellation_duration",
        default=24
    )
    show_advance_service = fields.Boolean(
        related="company_id.show_advance_service",
        readonly=False
    )

    # Constraints
    @api.multi
    @api.constrains('shift_exchange_duration')
    def _check_shift_exchange_duration(self):
        for res in self:
            if res.shift_exchange_duration <= 0:
                raise ValidationError(_(
                    "Shift exchange duration has to be bigger than 0."))
    @api.multi
    @api.constrains('shift_replacement_duration')
    def _check_shift_replacement_duration(self):
        for res in self:
            if res.shift_replacement_duration <= 0:
                raise ValidationError(_(
                    "Shift replacement duration has to be bigger than 0."))
