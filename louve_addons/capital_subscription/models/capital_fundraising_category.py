# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from datetime import datetime
import pytz


class CapitalFundraisingCategory(models.Model):
    _name = 'capital.fundraising.category'

    # Column Section
    name = fields.Char(string='Name', required=True)

    fundraising_id = fields.Many2one(
        comodel_name='capital.fundraising', string='Fundraising',
        required=True, ondelete='cascade', index=True, copy=False)

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        related='fundraising_id.company_id', store=True, readonly=True)

    product_id = fields.Many2one(
        comodel_name='product.product', string='Products', required=True,
        domain="[('is_capital_fundraising', '=', True)]")

    partner_account_id = fields.Many2one(
        comodel_name='account.account', string='Partner Account',
        domain=lambda self: [
            ('user_type_id.id', '=', self.env.ref(
                'account.data_account_type_receivable').id),
            ('deprecated', '=', False)], help="This account will be used"
        " instead of the default partner one, if defined.")

    capital_account_id = fields.Many2one(
        comodel_name='account.account', string='Final Capital Account',
        domain=lambda self: [
            ('user_type_id.id', '=', self.env.ref(
                'account.data_account_type_equity').id),
            ('deprecated', '=', False)], help="This account will be used"
        " to write a move between default product account and capital account"
        " when the payment is done.")

    refund_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Refund Account')

    deficit_product_id = fields.Many2one(
        'product.product',
        string='Deficit Share Product',
        domain=[('is_deficit_product', '=', True)])

    deficit_share_amount_ids = fields.One2many(
        comodel_name='capital.fundraising.deficit',
        inverse_name='fund_cate_id',
        string='Deficit Share')

    minimum_share_qty = fields.Integer(
        string='Minimum Share Quantity', required=True, default=1)

    line_ids = fields.One2many(
        comodel_name='capital.fundraising.category.line', string='Lines',
        inverse_name='fundraising_category_id')

    # Custom Section
    @api.multi
    def check_minimum_qty(self, partner):
        assert len(self) == 1, "Incorrect call"
        invoice_obj = self.env['account.invoice']
        category = self[0]
        # check minimum qty
        minimum_qty = category.minimum_share_qty

        # Compute just invoiced qty
        if partner.fundraising_partner_type_ids:
            for line in category.line_ids:
                if line.fundraising_partner_type_id.id in\
                        partner.fundraising_partner_type_ids.ids:
                    minimum_qty = min(line.minimum_share_qty, minimum_qty)

        # Compute previously computed qty
        category_ids = category.fundraising_id.category_ids.ids
        previous_invoices = invoice_obj.search([
            ('partner_id', '=', partner.id),
            ('state', 'in', ['open', 'paid']),
            ('fundraising_category_id', 'in', category_ids)])
        previous_qty = sum(
            previous_invoices.mapped('invoice_line_ids.quantity'))

        return minimum_qty - previous_qty

    @api.multi
    def get_deficit_share_amount(self, date_invoice):
        '''
        @Function to get the deficit share amount at the current time
        '''
        self.ensure_one()
        for deficit_amount in self.deficit_share_amount_ids:
            if (not deficit_amount.start_date or
                    deficit_amount.start_date <= date_invoice) and \
                    (not deficit_amount.end_date or
                     deficit_amount.end_date >= date_invoice):
                return deficit_amount.amount_by_share

        # Return zero in case no matched deficit amount found
        return 0
