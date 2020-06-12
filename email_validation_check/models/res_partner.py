# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
import logging
import random

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in range(20))


class ResPartner(models.Model):
    _inherit = 'res.partner'

    email_validation_string = fields.Char(
        string="String Validation Email",
        compute="_compute_email_validation_string",
        store=True,
    )
    is_checked_email = fields.Boolean(default=True)
    validation_url = fields.Char(
        'Link to validate',
        compute="_compute_validation_url",
        store=True,
    )
    show_send_email = fields.Boolean(
        compute="_compute_show_send_email",
        string="Show button send email confirm",
        store=True,
    )

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        no_check_validate_email = self._context.get('no_check_validate_email')
        if 'email' in vals and not no_check_validate_email:
            for partner in self.filtered('email'):
                if (
                    partner.validation_url
                    and (partner.is_interested_people or partner.is_member)
                    and not partner.supplier
                ):
                    mail_template = self.env.ref(
                        'email_validation_check.email_confirm_validate')
                    if mail_template:
                        mail_template.send_mail(self.id)
                    partner.is_checked_email = False
                # Update login user which's related partner
                user_related = self.env['res.users'].sudo().search([
                    ('partner_id', '=', partner.id)])
                user_related.write({'login': partner.email})
        return res

    @api.model
    def create(self, vals):
        no_check_validate_email = self._context.get('no_check_validate_email')
        res = super(ResPartner, self).create(vals)
        if res.validation_url and res.is_interested_people and \
                res.email and not res.supplier and not no_check_validate_email:
            mail_template = self.env.ref(
                'email_validation_check.email_confirm_validate')
            if mail_template:
                mail_template.send_mail(res.id)
            res.is_checked_email = False
        return res

    @api.multi
    @api.constrains('email')
    def check_exist_email(self):
        ignore_partner_ids = [
            self.env.ref('base.partner_root').id,
            self.env.ref('base.partner_admin').id,
        ]
        for partner in self.filtered('email'):
            if partner.supplier:
                continue
            if partner.id in ignore_partner_ids:
                continue
            if partner.user_ids:
                continue
            if partner.email:
                already_email = self.env['res.partner'].search([
                    ('email', '=', partner.email),
                    ('id', '!=', partner.id),
                    ('id', 'not in', ignore_partner_ids),
                    ('supplier', '=', False),
                ])
                if already_email:
                    raise ValidationError(_(
                        "Another user is already registered using this "
                        "email address: %s") % partner.email)

    @api.depends('email')
    def _compute_email_validation_string(self):
        for partner in self.filtered('email'):
            partner.email_validation_string = random_token()

    @api.multi
    @api.depends(
        'email', 'is_member', 'is_interested_people',
        'supplier', 'is_checked_email',
    )
    def _compute_show_send_email(self):
        for partner in self:
            if (
                partner.supplier
                or not partner.email
                or partner.is_checked_email
                or (not partner.is_member and not partner.is_interested_people)
            ):
                partner.show_send_email = False
            else:
                partner.show_send_email = True

    @api.multi
    def check_email_validation_string(self, string):
        for partner in self:
            if partner.email_validation_string == string:
                partner.is_checked_email = True
                partner.show_send_email = False
                return True
            else:
                return False

    @api.multi
    def recompute_hash_confirm_email(self):
        mail_template = self.env.ref(
            'email_validation_check.email_confirm_validate')
        for partner in self:
            curr_hash = partner.email_validation_string
            partner.email_validation_string = random_token()
            if partner.email_validation_string != curr_hash:
                if mail_template:
                    mail_template.send_mail(self.id)
        return True

    @api.depends('email_validation_string')
    def _compute_validation_url(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        base_url = get_param('web.base.url')
        for partner in self:
            partner.validation_url = '%s/validate/%s/%s' % (
                    base_url,
                    partner.id,
                    partner.email_validation_string,
                )
