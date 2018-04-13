# -*- coding: utf-8 -*-


from openerp import api
from openerp.osv import fields, osv


class stock_inventory(osv.osv):
    _inherit = 'stock.inventory'

    def post_inventory(self, cr, uid, inv, context=None):
        res = super(stock_inventory, self).post_inventory(
            cr, uid, inv, context=context)
        if inv:
            move_obj = self.pool.get('stock.move')
            date_inv = inv.date
            move_ids = inv.move_ids.ids
            move_obj.write(cr, uid, move_ids, {'date': date_inv},
                           context=context)
        return res
