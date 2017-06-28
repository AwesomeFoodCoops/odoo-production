# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    partner_owned_share_id = fields.Many2one('res.partner.owned.share',
                                             string="Partner Owned Share",
                                             readonly=True)

    @api.model
    def create(self, vals):
        '''
        Modify the function to:
            - Assign the Partner Own Share for invoice with category assigned
        '''
        res = super(AccountInvoice, self).create(vals)

        if vals.get('fundraising_category_id'):
            res.assign_ownshare_to_invoice()
        return res

    @api.multi
    def write(self, vals):
        '''
        Modify the function to:
            - Reassign the partner own share for invoice with partner or
            fundraising category changed (Fundraising transfer case)
        '''
        res = super(AccountInvoice, self).write(vals)
        if 'partner_id' in vals or 'fundraising_category_id' in vals:
            for invoice in self:
                invoice.assign_ownshare_to_invoice()
        return res

    @api.multi
    def assign_ownshare_to_invoice(self):
        '''
        @Function used for assigning an owned share record to invoices
        '''
        partner_owned_share_env = self.env['res.partner.owned.share']
        for invoice in self:
            fundraising_category = invoice.fundraising_category_id
            if not fundraising_category:
                continue

            # Search for existing partner owned share
            owned_share = partner_owned_share_env.sudo().search(
                [('partner_id', '=', invoice.partner_id.id),
                 ('category_id', '=', fundraising_category.id)],
                limit=1)

            # Create a new partner owned share if not exists
            if not owned_share:
                owned_share_vals = {
                    'partner_id': invoice.partner_id.id,
                    'category_id': fundraising_category.id,
                }
                owned_share = partner_owned_share_env.sudo().create(
                    owned_share_vals)

            invoice.partner_owned_share_id = owned_share.id

        return True
