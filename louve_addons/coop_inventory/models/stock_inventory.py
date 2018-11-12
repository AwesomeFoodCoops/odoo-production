# -*- coding: utf-8 -*-
from openerp import api, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def _get_inventory_lines(self, inventory):
        vals = super(StockInventory, self)._get_inventory_lines(inventory)
        product_obj = self.env['product.product']
        fixed_vals = []
        for val in vals:
            product_id = val['product_id']
            product = product_obj.browse(product_id)
            if not product.type == 'product':
                continue
            fixed_vals.append(val)
        return fixed_vals
