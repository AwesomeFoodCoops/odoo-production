# -*- coding: utf-8 -*-

from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    """
    Override native method to prevent from receiving consumable products
    after approved purchase orders
    """
    @api.multi
    def _create_picking(self):
        for order in self:
            if any([ptype in ['product'] for ptype in
                    order.order_line.mapped('product_id.type')]):
                res = order._prepare_picking()
                picking = self.env['stock.picking'].create(res)
                stockable_lines = order.order_line.filtered(
                    lambda r: r.product_id.type in ['product'])
                moves = stockable_lines._create_stock_moves(picking)
                move_ids = moves.action_confirm()
                moves = self.env['stock.move'].browse(move_ids)
                seq = 0
                for move in sorted(moves, key=lambda m: m.date_expected):
                    seq += 5
                    move.sequence = seq
                moves.force_assign()
        return True
