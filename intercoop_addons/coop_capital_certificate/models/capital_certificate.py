# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


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
        string="Certificate Lines", comodel_name="capital.certificate.line",
        inverse_name="certificate_id")

    @api.multi
    @api.constrains('partner_id', 'year')
    def _unique_partner_year(self):
        for certificate in self:
            if self.search_count([
                ('partner_id', '=', self.partner_id.id),
                ('year', '=', self.year),
            ]) > 1:
                raise ValidationError(_(
                    "Partner %s already has a certificate for year %s!" % (
                        certificate.partner_id.name, certificate.year)))

    @api.multi
    def create_certificate(self, send_mail=False):
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

        Attachment = self.env['ir.attachment']
        attachment_vals = self._prepare_attachment(values)
        attachment_ids = Attachment.create(attachment_vals)

        if send_mail:
            Mail = self.env['mail.mail']
            mail_vals = self._prepare_mail(values, attachment_ids)
            mail = Mail.create(mail_vals)
            mail.send()

    @api.multi
    def _prepare_attachment(self, values={}):
        self.ensure_one()
        return {
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

    @api.multi
    def _prepare_mail(self, values={}, attachment_ids=None):
        self.ensure_one()
        email_to = ",".join([p.email for p in self.env['res.partner'].browse(
            values['partner_ids'])])
        return {
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
        }


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
