from odoo import api, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.multi
    def post_inventory(self):
        res = super(StockInventory, self).post_inventory()
        for inv in self:
            if inv.move_ids:
                inv.move_ids.write({'date': inv.date})
        return res
