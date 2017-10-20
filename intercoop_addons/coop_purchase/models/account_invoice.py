# -*- coding: utf-8 -*-

from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        res = super(AccountInvoice, self).purchase_order_change()
        for line in self.invoice_line_ids:
            suppliers = line.product_id.seller_ids.filtered(
                lambda x: x.name == self.partner_id)
            if suppliers:
                line.base_price = suppliers[0].base_price
        return res
