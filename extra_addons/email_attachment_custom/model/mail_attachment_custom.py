# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models


class MailAttachmentCustom(models.Model):
    _name = 'mail.attachment.custom'

    name = fields.Char(required=True, string="Description")
    mail_template_id = fields.Many2one(
        "mail.template",
        string="Email Template")
    condition = fields.Char(
        string="Condition",
        help="""Specify the condition to add the attachment in the email. If no
        condition specified, the attachments will be added by default.
        Example: ${object.partner_id.customer}
        """)
    active = fields.Boolean(string="Active", default=True)
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "mail_attachment_custom_attachment_rel"
        "mail_attachment_custom_id",
        "attachment_id",
        string="Attachments")
