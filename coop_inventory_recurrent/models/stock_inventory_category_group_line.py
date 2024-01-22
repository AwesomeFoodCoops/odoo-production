# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models


class StockInventoryCategoryGroupLine(models.Model):
    _name = "stock.inventory.category.group.line"
    _description = "Category Group Line"

    group_id = fields.Many2one(
        comodel_name="stock.inventory.category.group",
        ondelete="cascade"
    )
    category_id = fields.Many2one(
        'product.category', string='Product category',
        required=True
    )
    copies = fields.Selection([
        ('1', '1'),
        ('2', '2'),
    ], required=True, default='2')
