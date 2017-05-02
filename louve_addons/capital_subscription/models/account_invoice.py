# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Column Section
    is_capital_fundraising = fields.Boolean(
        string='Concerns Capital Fundraising')

    fundraising_category_id = fields.Many2one(
        comodel_name='capital.fundraising.category',
        string='Fundraising Category')

    # Overload Section
    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None, date=None, description=None,
            journal_id=None):
        res = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        res['is_capital_fundraising'] = invoice.is_capital_fundraising
        res['fundraising_category_id'] = invoice.fundraising_category_id.id
        return res

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        invoice_id = move_lines[0][2]['invoice_id']
        if self.browse(invoice_id).is_capital_fundraising:
            for i in range(len(move_lines)):
                product_id = move_lines[i][2]['product_id']
                if product_id:
                    break
            if product_id:
                for i in range(len(move_lines)):
                    move_lines[i][2]['product_id'] = product_id
        return move_lines

    # Constraint Section
    @api.one
    @api.constrains(
        'is_capital_fundraising', 'fundraising_category_id',
        'partner_id', 'invoice_line_ids')
    def _check_capital_fundraising(self):
        invoice = self
        product_ids = invoice.invoice_line_ids.mapped('product_id.id')

        if invoice.is_capital_fundraising:
            # Check mandatory field
            if not invoice.fundraising_category_id:
                raise exceptions.UserError(_(
                    "A Capital fundraising must have a capital category"
                    " defined"))

            # Check products
            forbidden_product_ids =\
                list(set(product_ids) - set(
                    [invoice.fundraising_category_id.product_id.id]))
            if forbidden_product_ids:
                forbidden_products = self.env['product.product'].browse(
                    forbidden_product_ids)
                raise exceptions.UserError(_(
                    "%s category do not allow %s products") % (
                    invoice.fundraising_category_id.name, ', '.join(
                        forbidden_products.mapped('name'))))

            ordered_qty = sum(invoice.invoice_line_ids.mapped('quantity'))

            to_order_qty = invoice.fundraising_category_id.check_minimum_qty(
                invoice.partner_id)

            if ordered_qty < to_order_qty:
                raise exceptions.UserError(_(
                    "This category and (previous orders) requires at least"
                    " %d shares.") % (to_order_qty))
        else:
            capital_product_ids = self.env['product.product'].search(
                [('is_capital_fundraising', '=', True)]).ids
            forbidden_product_ids =\
                list(set(product_ids).intersection(capital_product_ids))
            if forbidden_product_ids:
                forbidden_product_names = ', '.join(
                    self.env['product.product'].browse(
                        forbidden_product_ids).mapped('name'))
                raise exceptions.UserError(_(
                    "Non capital invoice do not accept line with capital"
                    " subscription products : %s") % (forbidden_product_names))

    # OnChange Section
    @api.onchange('fundraising_category_id')
    def onchange_fundraising_category_id(self):
        if self.fundraising_category_id:
            self.journal_id = \
                self.fundraising_category_id.fundraising_id.journal_id
            if self.fundraising_category_id.partner_account_id:
                self.account_id =\
                    self.fundraising_category_id.partner_account_id
