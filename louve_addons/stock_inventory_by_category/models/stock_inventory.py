# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, _


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _get_available_filters(self):
        res_filter = super(StockInventory, self)._get_available_filters()
        res_filter.append(('category', _('Choose categories')))
        return res_filter

    category_ids = fields.Many2many(
        'product.category', 'stock_inventory_category_rel', 'inventory_id',
        'category_id', 'Inventoried Categories', readonly=True,
        states={'draft': [('readonly', False)]},
        help="Specify Categories to focus your inventory on.")
    filter = fields.Selection(_get_available_filters)

    def _get_inventory_lines(self, cr, uid, inventory, context=None):
        vals = super(StockInventory, self)._get_inventory_lines(
            cr, uid, inventory, context=context)
        if inventory.filter == 'category'and inventory.category_ids:
            location_obj = self.pool.get('stock.location')
            product_obj = self.pool.get('product.product')
            location_ids = location_obj.search(
                cr, uid, [('id', 'child_of', [inventory.location_id.id])],
                context=context)
            domain = ' location_id in %s'
            args = (tuple(location_ids),)
            products = product_obj.search(
                cr, uid,
                [('categ_id', 'in', [c.id for c in inventory.category_ids])],
                context=context)
            domain += ' and product_id In %s'
            args += (tuple(products),)
            cr.execute('''
               SELECT product_id, sum(qty) as product_qty, location_id,
               lot_id as prod_lot_id, package_id, owner_id as partner_id
               FROM stock_quant WHERE''' + domain + '''
               GROUP BY product_id, location_id, lot_id, package_id, partner_id
            ''', args)
            vals = []
            for product_line in cr.dictfetchall():
                for key, value in product_line.items():
                    if not value:
                        product_line[key] = False
                product_line['inventory_id'] = inventory.id
                product_line['theoretical_qty'] = product_line['product_qty']
                if product_line['product_id']:
                    product = product_obj.browse(
                        cr, uid, product_line['product_id'], context=context)
                    product_line['product_uom_id'] = product.uom_id.id
                vals.append(product_line)
        return vals
