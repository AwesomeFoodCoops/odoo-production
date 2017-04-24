# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class CapitalCertificate(models.Model):
    _name = "capital.certificate"

    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True, ondelete='cascade')
    year = fields.Integer(string="Year", required=True)
    template_id = fields.Many2one(
        'mail.template', string='Email to Send', required=True,
        ondelete='restrict', help="""This field contains the template of the"""
        """ mail that will be automatically sent""")
    line_ids = fields.One2many(
        string="Lines", comodel_name="capital.certificate.line",
        inverse_name="certificate_id")

    @api.multi
    def execute(self):
        self.ensure_one()
        res_id = self.id
        template_id = self.template_id.id
        fields = [
            'subject', 'body_html', 'email_from', 'email_to', 'partner_to',
            'email_cc', 'reply_to', 'attachment_ids', 'mail_server_id']
        returned_fields = fields + ['partner_ids', 'attachments']
        template_values = self.env['mail.template'].with_context(
            tpl_partners_only=True).browse(template_id).generate_email(
            res_id, fields=fields)
        values = dict(
            (field, template_values[field])
            for field in returned_fields
            if template_values.get(field))
        values['body'] = values.pop('body_html', '')

        Mail = self.env['mail.mail']
        Attachment = self.env['ir.attachment']
        email_to = ",".join([p.email for p in self.env['res.partner'].browse(
            values['partner_ids'])])
        vals = {
            'name': (self.partner_id.name + ' - ' + str(self.year) +
                     '.pdf').replace(',', ''),
            'datas_fname': (self.partner_id.name + ' - ' + str(self.year) +
                            '.pdf').replace(',', ''),
            'res_model': 'capital.certificate',
            'res_id': self.id,
            'mimetype': 'application/pdf',
            'index_content': 'application',
            'public': False,
            'datas': values['attachments'][0][1],
        }
        attachment_ids = Attachment.create(vals)
        mail = Mail.create({
            'body_html': values['body'],
            'email_to': email_to,
            'recipient_ids': (0, 0, values['partner_ids']),
            'auto_delete': True,
            'subject': values['subject'],
            'model': 'capital.certificate',
            'res_id': self.id,
            'email_from': values['email_from'],
            'reply_to': values['reply_to'],
            'attachment_ids': [(6, 0, [a.id for a in attachment_ids])],
            'mail_server_id': self.env['ir.mail_server'].search([])[0].id
        })
        mail.send()
        return values


class CapitalCertificateLine(models.Model):
    _name = "capital.certificate.line"

    account_move_line_id = fields.Many2one(
        string="Account Move Line", comodel_name="account.move.line")
    certificate_id = fields.Many2one(
        string="Certificate", comodel_name="capital.certificate")
    date = fields.Date("Invoice Date")
    payment_date = fields.Date("Payment Date")
    qty = fields.Integer("Quantity")
    product = fields.Char("Category")
    price = fields.Float("Unit Price")
