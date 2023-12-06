# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import fields, models, api

BADGE_PARTNER_BOOTSTRAP_COOPERATIVE_STATE = [
    ("success", "OK"),
    ("warning", "Warning"),
    ("danger", "Danger"),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    MAPPING_COOPERATIVE_STATE = {
        "up_to_date": "success",
        "alert": "warning",
        "delay": "warning",
        "suspended": "danger",
        "not_concerned": "danger",
        "blocked": "danger",
        "unpayed": "danger",
        "unsubscribed": "danger",
        "exempted": "success",
    }
    next_shift_time = fields.Datetime(
        compute="_compute_next_shift_time"
    )
    bootstrap_cooperative_state = fields.Selection(
        compute="_compute_bootstrap_cooperative_state",
        string="Bootstrap State",
        store=True,
        selection=BADGE_PARTNER_BOOTSTRAP_COOPERATIVE_STATE,
    )

    # Compute Section
    @api.depends("cooperative_state")
    @api.multi
    def _compute_bootstrap_cooperative_state(self):
        for partner in self:
            partner.bootstrap_cooperative_state = \
                self.MAPPING_COOPERATIVE_STATE.get(
                    partner.cooperative_state, "danger"
                )

    @api.multi
    def update_boostrap_partner_state(self):
        for record in self:
            record._compute_bootstrap_cooperative_state()
        return True

    @api.multi
    def _compute_next_shift_time(self):
        for partner in self:
            next_shift_time, _next_shift_date = partner.get_next_shift_date()
            partner.next_shift_time = next_shift_time

    # Custom Section
    @api.multi
    def log_move(self, action):
        self.ensure_one()
        partner_move_obj = self.env["res.partner.move"]
        partner_alert_obj = self.env["res.partner.alert"]
        partner_alert_mail_template = self.env.ref(
            "coop_badge_reader.email_template_partner_alert"
        )
        for partner in self:
            partner_move_obj.create({
                "partner_id": partner.id,
                "cooperative_state": partner.cooperative_state,
                "action": action,
                "bootstrap_cooperative_state":
                    partner.bootstrap_cooperative_state,
            })
            if partner_alert_mail_template and action == "in":
                partner_alerts = partner_alert_obj.search(
                    [
                        ("expected_member_id", "=", partner.id),
                        ("state", "=", "open"),
                    ]
                )

                for partner_alert in partner_alerts:
                    partner_alert_mail_template.send_mail(
                        res_id=partner_alert.id, force_send=True
                    )

    @api.multi
    def action_grace_partner(self):
        """
        @Function call when gracing a partner:
            Creating Extension for partner
                - Start Date: Current Date
                - End Date:
                    Current Date + Duration
                    If End Date exceeds the next Shift Time, End Date will
                    be the next shift time
        """
        self.ensure_one()
        current_extension = self.extension_ids.filtered("current_extension")
        if current_extension:
            return current_extension[0].date_stop
        # Only grace extensions for suspended user with no extension
        if self.cooperative_state != "suspended":
            return False
        shift_ext_env = self.env["shift.extension"]
        ext_type_env = self.env["shift.extension.type"]
        date_start_str = fields.Date.context_today(self)
        grace_ext_type = ext_type_env.sudo().search(
            [("is_grace_period", "=", True),
             "|",
             ('extension_method', '=', 'to_next_regular_shift'),
             ('duration', '>', 0)], limit=1
        )
        if not grace_ext_type:
            return False

        # No add extension when previous state is Delay (Delay -> Suspended)
        # Condition: Last extension date > Alert date (Alert date must be set)
        if self.date_alert_stop:
            last_extension_date = False
            if self.extension_ids:
                exts = self.extension_ids.sorted("date_stop", True)
                last_extension_date = exts[0].date_stop
                if last_extension_date > self.date_alert_stop:
                    return False

        date_stop_str = date_start_str + timedelta(
            days=grace_ext_type.duration
        )
        _next_shift_time, next_shift_date = self.get_next_shift_date()
        if next_shift_date:
            # Set the next shift date as the end date if the end date exceed
            # the next shift date
            next_shift_date = fields.Date.from_string(next_shift_date)
            next_shift_date += timedelta(days=1)
            if date_stop_str > next_shift_date or \
                    grace_ext_type.extension_method == "to_next_regular_shift":
                date_stop_str = next_shift_date
        if date_stop_str <= date_start_str:
            # No create extension when duration<=0 and extension_method is Fixed
            return False

        # Create extension
        res = shift_ext_env.sudo().create(
            {
                "date_start": date_start_str,
                "date_stop": date_stop_str,
                "partner_id": self.id,
                "type_id": grace_ext_type.id,
            }
        )
        return res.date_stop

    @api.multi
    def set_badge_distributed(self):
        for partner in self:
            partner.badge_distribution_date = fields.Date.context_today(self)
        return True
