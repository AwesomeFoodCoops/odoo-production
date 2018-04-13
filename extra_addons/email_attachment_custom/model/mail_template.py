# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    mail_attachment_custom_ids = fields.One2many(
        'mail.attachment.custom',
        "mail_template_id",
        string="Custom Attachments")

    @api.multi
    def send_mail(self, res_id, force_send=False, raise_exception=False):
        self.ensure_one()

        # Collect attachments
        attachment_ids = []
        for custom_att_conf in self.mail_attachment_custom_ids:
            if not custom_att_conf.active:
                continue
            if not custom_att_conf.condition:
                attachment_ids += custom_att_conf.attachment_ids.ids
                continue

            condition_res = self.render_template(
                template_txt=custom_att_conf.condition,
                model=self.model, res_ids=res_id)

            condition = False
            try:
                condition = safe_eval(condition_res)
            except:
                # If evaling is not possible
                if condition_res:
                    condition = True
            if condition:
                attachment_ids += custom_att_conf.attachment_ids.ids

        # Call super without force send
        res_mail_id = super(MailTemplate, self).send_mail(
            res_id=res_id, force_send=False, raise_exception=raise_exception)

        mail = self.env['mail.mail'].browse(res_mail_id)
        for att_id in attachment_ids:
            mail.attachment_ids = [(4, att_id)]

        if force_send:
            mail.send(raise_exception=raise_exception)

        return res_mail_id
