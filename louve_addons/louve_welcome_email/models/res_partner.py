# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models
from openerp.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def send_welcome_email(self):
        mail_template = self.env.ref('coop_membership.welcome_email')
        if not mail_template:
            return False

        attachment_params = \
            self.env.ref(
                'louve_welcome_email.welcome_email_attachment_list').value
        attachment_params = safe_eval(attachment_params)

        for partner in self:
            attachment_list = attachment_params.get(partner.shift_type, [])
            attachment_ids = []

            for filename in attachment_list:
                attachment = self.env['ir.attachment'].search([
                    ('name', 'like', filename)], limit=1)

                if attachment:
                    attachment_ids.append(attachment.id)

            mail_id = mail_template.send_mail(partner.id)
            mail = self.env['mail.mail'].browse(mail_id)
            if attachment:
                mail.attachment_ids = [(6, 0, attachment_ids)]
            partner.welcome_email = True
        return True
