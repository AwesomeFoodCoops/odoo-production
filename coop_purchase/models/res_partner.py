from lxml import etree
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    show_discount = fields.Boolean("Show discounts on update prices")

    discount_computation = fields.Selection(
        selection=[('total', 'Total'), ('unit_price', 'Unit Price')],
        string="Discount Computation")
