# -*- coding: utf-8 -*-

from openerp import models, api, fields
from openerp.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    base_price = fields.Monetary(
        string="Base Price",
        digits=dp.get_precision('Product Price')
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        ret = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.invoice_id.type in ('in_invoice', 'in_refund') and \
                self.product_id:
            suppliers = self.product_id.seller_ids.filtered(
                lambda x: x.name == self.partner_id)
            if suppliers:
                self.package_qty = suppliers[0].package_qty
                self.discount = suppliers[0].discount
                self.base_price = suppliers[0].base_price
                self.price_unit = suppliers[0].price
        return ret

    @api.model
    def new(self, values=None):
        """
        Only apply the linked to a purchase.order.line.discount to the
        account_invoice_line when invoice lines have no discount
        """
        values = {} if values is None else values
        discount = values.get('discount', 0)
        account_invoice_line = super(
            AccountInvoiceLine, self).new(values=values)
        if discount:
            account_invoice_line.discount = discount
        return account_invoice_line
