# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    delivery_categ_ids = fields.Many2many(
        comodel_name='delivery.category',
        string='Delivery Categories',
        relation="delivery_category_product",
        column1="pid",
        column2="cid",
    )
