# -*- coding: utf-8 -*-

from openerp import models, api, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    base_price = fields.Monetary("Base Price")

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
