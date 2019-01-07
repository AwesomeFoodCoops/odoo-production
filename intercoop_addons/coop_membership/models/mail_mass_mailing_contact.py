# -*- coding: utf-8 -*-

from openerp import api, fields, models


class MailMassMailingContact(models.Model):
    _inherit = 'mail.mass_mailing.contact'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('is_worker_member', '=', True)],
        string='Number'
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.partner_id.name
            self.email = self.partner_id.email
