from odoo import models, api, fields
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    base_price = fields.Monetary(digits=dp.get_precision("Product Price"))

    @api.onchange("product_id")
    def _onchange_product_id(self):
        ret = super()._onchange_product_id()
        if (
            self.invoice_id.type in ("in_invoice", "in_refund")
            and self.product_id
        ):
            suppliers = self.product_id.seller_ids.filtered(
                lambda x: x.name == self.partner_id
            )
            if suppliers:
                self.package_qty = suppliers[0].package_qty
                self.discount = suppliers[0].discount
                self.base_price = suppliers[0].base_price
                self.price_unit = suppliers[0].price
        return ret

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)

        # Rounding the price based on the partner discount computation
        # for supplier invoice or supplier refund
        if self.invoice_id.type in ['in_invoice', 'in_refund'] and \
            self.discount and \
                self.invoice_id.partner_id.discount_computation == \
                'unit_price':
            price = currency.round(price)

        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(
                price, currency, self.quantity, product=self.product_id,
                partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = \
            taxes['total_excluded'] if taxes else self.quantity * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and \
                self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            currency = self.invoice_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            price_subtotal_signed = currency._convert(
                price_subtotal_signed, self.invoice_id.company_id.currency_id,
                self.company_id or self.env.user.company_id, date or fields.Date.today())
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
