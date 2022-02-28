from odoo import models, api, fields
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    date_invoice = fields.Date(
        related="invoice_id.date_invoice"
    )
    product_categ_id = fields.Many2one(
        comodel_name="product.category",
        related="product_id.categ_id"
    )
