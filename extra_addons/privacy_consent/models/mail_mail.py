# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, models


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.multi
    def _postprocess_sent_message(self, mail_sent=True):
        """Write consent status after sending message."""
        if mail_sent and self.env.context.get('mark_consent_sent'):
            # Get all mails sent to consents
            consent_mails = self.filtered(
                lambda one: one.mail_message_id.model == "privacy.consent"
            )
            # Get related draft consents
            consents = self.env["privacy.consent"].browse(
                consent_mails.mapped("mail_message_id.res_id")
            ).filtered(lambda one: one.state == "draft")
            # Set as sent
            consents.write({
                "state": "sent",
            })
        return super(MailMail, self)._postprocess_sent_message(mail_sent)

    @api.multi
    def send_get_mail_body(self, partner=None):
        """Replace privacy consent magic links.

        This replacement is done here instead of directly writing it into
        the ``mail.template`` to avoid writing the tokeinzed URL
        in the mail thread for the ``privacy.consent`` record,
        which would enable any reader of such thread to impersonate the
        subject and choose in its behalf.
        """
        result = super(MailMail, self).send_get_mail_body(partner=partner)
        # Avoid polluting other model mails
        if self.env.context.get("active_model") != "privacy.consent":
            return result
        # Tokenize consent links
        consent = self.env["privacy.consent"].browse(
            self.mail_message_id.res_id)
        result = result.replace(
            "/privacy/consent/accept/",
            consent._url(True),
        )
        result = result.replace(
            "/privacy/consent/reject/",
            consent._url(False),
        )
        return result
