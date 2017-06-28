# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models


class ResPartnerOwnedShare(models.Model):
    _name = 'res.partner.owned.share'

    name = fields.Char('Name',
                       compute="_compute_partner_owned_share_name",
                       store=True)

    partner_id = fields.Many2one('res.partner',
                                 string="Partner",
                                 required=True,
                                 readonly=True)
    category_id = fields.Many2one('capital.fundraising.category',
                                  string="Category", required=True,
                                  readonly=True)
    owned_share = fields.Integer(string='Owned Share',
                                 compute="_compute_owned_share",
                                 readonly=True,
                                 store=True)
    related_invoice_ids = fields.One2many('account.invoice',
                                          'partner_owned_share_id',
                                          string="Related Invoices")

    @api.multi
    @api.depends('related_invoice_ids',
                 'related_invoice_ids.state')
    def _compute_owned_share(self):
        '''
        @Function to compute the owned share based on related Invoice
        '''
        for partner_share in self:
            owned_share = 0
            for invoice in partner_share.related_invoice_ids:
                if invoice.state in ['open', 'paid']:
                    if invoice.type == 'out_invoice':
                        owned_share += sum(
                            invoice.mapped('invoice_line_ids.quantity'))
                    else:
                        owned_share -= sum(
                            invoice.mapped('invoice_line_ids.quantity'))
            partner_share.owned_share = owned_share

    @api.multi
    @api.depends('partner_id', 'partner_id.name',
                 'category_id', 'category_id.name')
    def _compute_partner_owned_share_name(self):
        '''
        @Function to compute the name for partner owned share
            - Partner_name - Category Name
        '''
        for partner_share in self:
            partner_name = partner_share.partner_id.name or ''
            category_name = partner_share.category_id.name or ''
            partner_share.name = '%s - %s' % (partner_name, category_name)
