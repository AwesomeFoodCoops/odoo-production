# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models


class StockInventoryCategoryGroup(models.Model):
    _name = "stock.inventory.category.group"
    _description = "Category Group"

    name = fields.Char(required=True)
    category_ids = fields.Many2many(
        'product.category', string='Product categories'
    )
    line_ids = fields.One2many(
        "stock.inventory.category.group.line",
        "group_id"
    )

    @api.onchange('category_ids')
    def onchange_category_ids(self):
        categs = self.mapped('line_ids.category_id')
        GroupLine = self.env['stock.inventory.category.group.line']
        for categ in self.category_ids:
            if categ not in categs:
                line = GroupLine.new({
                    'category_id': categ.id,
                    'copies': '2'
                })
                line.default_get(
                    GroupLine.fields_get().keys())
                self.line_ids |= line
