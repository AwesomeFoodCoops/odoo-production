from datetime import datetime, timedelta

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ShiftRegistration(models.Model):
    _inherit = "shift.registration"

    @api.multi
    def check_shift_regis_cancelable(self):
        for record in self:
            if record.state in ('waiting', 'cancel'):
                return False
        return True

    @api.multi
    def cancel_shift_regis_from_market(self):
        if not self.check_shift_regis_cancelable():
            return 0, ''
        mail_template = self.env.ref(
            "coop_memberspace.shift_registration_cancel_email")
        SCEvent = self.env['shift.counter.event'].sudo().with_context(
            automatic=True,
        )
        for record in self:
            """
            F#T60472 - [TMT] Fix for malus points when cancelling a shift
            ==> Add point counter when closing a shift
            if record.shift_type == "standard":
                vals = {
                    'name': _('Annuler votre participation'),
                    'type': 'standard',
                    'partner_id': record.partner_id.id,
                    'point_qty': -1,
                    'shift_id': record.shift_id.id
                }
                if record.partner_id.final_ftop_point > 0:
                    vals["type"] = "ftop"
                SCEvent.create(vals)
            """
            # Cancel registration
            record.with_context(bypass_reason=1).button_reg_cancel()
            mail_template.send_mail(record.id)
        return 1, ''

    @api.model
    def get_upcoming(self, partner, args=[]):
        # Count the cancelled registrations also.
        args += [
            ("partner_id", "=", partner.id),
            #("state", "not in", ["cancel"]),
            #("exchange_state", "!=", "replacing"),
            (
                "date_begin",
                ">=",
                datetime.now(),
            ),
        ]

        shift_upcomming = self.sudo().search(args,
            order="date_begin",
        )
        return shift_upcomming
