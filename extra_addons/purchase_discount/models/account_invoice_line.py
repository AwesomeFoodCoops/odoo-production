# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import api, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def new(self, values=None):
        """
        Apply the linked to a purchase.order.line.discount to the
        account_invoice_line
        """
        values = {} if values is None else values
        account_invoice_line = super(
            AccountInvoiceLine, self).new(values=values)
        if account_invoice_line.purchase_line_id:
            account_invoice_line.discount =\
                account_invoice_line.purchase_line_id.discount
        return account_invoice_line

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id', 'invoice_id.company_id')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)

        # Rounding the price based on the partner discount computation
        # for supplier invoice or supplier refund
        if self.invoice_id.type in ['in_invoice', 'in_refund'] and \
                self.invoice_id.partner_id.discount_computation == \
                'unit_price':
            price = currency.round(price)

        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(
                price, currency, self.quantity,
                product=self.product_id,
                partner=self.invoice_id.partner_id)

        self.price_subtotal = price_subtotal_signed =\
            taxes['total_excluded'] if taxes else\
            self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.currency_id !=\
                self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.compute(
                price_subtotal_signed,
                self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1\
            or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
