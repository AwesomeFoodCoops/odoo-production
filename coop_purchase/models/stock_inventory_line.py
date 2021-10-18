# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    product_default_code = fields.Char(
        string="Internal Reference",
        related="product_id.default_code",
        store=True
    )
