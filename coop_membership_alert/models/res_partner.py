
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    alert_mail_count = fields.Integer()
    suspened_mail_count = fields.Integer()

    @api.model
    def cron_send_alert_email(self, max_count=1, limit=200):
        mail_template = self.env.ref("coop_membership_alert.email_member_alert", False)
        if not mail_template:
            return
        self.env.cr.execute(
            # Clean counted value if not alert anymore
            """
                UPDATE res_partner
                SET alert_mail_count = 0
                WHERE cooperative_state != 'alert'
                    AND alert_mail_count > 0
            """
        )
        members = self.search(
            [
                ("cooperative_state", "=", "alert"),
                ("email", "!=", False),
                ("date_alert_stop", ">=", fields.Date.today()),
                "|",
                ("alert_mail_count", "=", False),  # Case of old data
                ("alert_mail_count", "<", max_count)
            ],
            limit=limit, order="write_date"
        )

        for member in members:
            mail_template.send_mail(member.id, force_send=True)
            member.alert_mail_count += 1
            member.message_post(body=_("Message d'alerte envoyé"))

    @api.model
    def cron_send_suspended_email(self, max_count=1, limit=200):
        mail_template = self.env.ref("coop_membership_alert.email_member_suspended", False)
        if mail_template:
            self.env.cr.execute(
                # Clean counted value if not suspended anymore
                """
                    UPDATE res_partner
                    SET suspened_mail_count = 0
                    WHERE cooperative_state != 'suspended'
                        AND suspened_mail_count > 0
                """
            )
            members = self.get_suspended_members(max_count=max_count, limit=limit, set_count=True)
            if members:
                mail_template.with_context(
                    members=members,
                    max_count=max_count,
                    limit=limit,
                ).send_mail(self.env.user.partner_id.id, force_send=True)

    def get_suspended_members(self, max_count=1, limit=200, set_count=False):
        members = self.search(
            [
                ("cooperative_state", "=", "suspended"),
                ("email", "!=", False),
                ("date_alert_stop", "<=", fields.Date.today()),
                "|",
                ("suspened_mail_count", "=", False),  # Case of old data
                ("suspened_mail_count", "<", max_count)
            ],
            limit=limit, order="write_date"
        )
        if set_count:
            for member in members:
                member.suspened_mail_count += 1
        return list(members)

    def get_mail_template_signature(self):
        return self.env.user.company_id.name

    def get_partner_firstlast_name(self):
        self.ensure_one()
        # Case 1: installed module partner_firstname
        if hasattr(self, "firstname") and hasattr(self, "lastname"):
            return self.firstname or "", self.lastname or ""
        # Case 2: default
        name_parts = self.name.split(",")
        if len(name_parts) > 1:
            return name_parts[1].strip(), name_parts[0].strip()
        return self.name, ""
