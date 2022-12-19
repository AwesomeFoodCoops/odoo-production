# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models


class DeliveryCategory(models.Model):
    _name = "delivery.category"
    _description = "Delivery Category"

    name = fields.Char(required=True)
    product_ids = fields.Many2many(
        comodel_name='product.template',
        string='Products',
        relation="delivery_category_product",
        column1="cid",
        column2="pid",
    )
