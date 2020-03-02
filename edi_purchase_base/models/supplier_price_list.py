# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models, fields
import odoo.addons.decimal_precision as dp


class SupplierPriceList(models.Model):
    _name = "supplier.price.list"

    import_date = fields.Date(string="Import date", readonly=True)
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="EDI Supplier",
        domain="[('is_edi', '=', True), ('supplier', '=', True)]",
        readonly=True,
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template", string="Product"
    )
    product_name = fields.Char(
        string="Product name", readonly=True, required=True
    )
    supplier_code = fields.Char(
        string="Supplier code", readonly=True, required=True
    )
    price = fields.Float(
        "Price",
        digits_compute=dp.get_precision("Product Price"),
        readonly=True,
        required=True,
        help="The price HT to purchase a product",
    )
    apply_date = fields.Date(string="Apply date", readonly=True, required=True)
