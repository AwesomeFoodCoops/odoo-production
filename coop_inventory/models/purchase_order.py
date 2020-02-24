from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    """
    Override native method to prevent from receiving consumable products
    after approved purchase orders
    """

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product'] for ptype in
                    order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(
                    lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                stockable_lines = order.order_line.filtered(
                    lambda r: r.product_id.type in ["product"]
                )
                moves = stockable_lines._create_stock_moves(picking)
                moves = moves.filtered(
                    lambda x: x.state not in ('done', 'cancel')
                )._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id,
                )
        return True
