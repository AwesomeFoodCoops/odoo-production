# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        for picking in self:
            pack_pickings = picking.pack_operation_product_ids
            pack_moves = picking.move_lines.mapped(
                'linked_move_operation_ids.operation_id')
            diff_pack_op = pack_pickings - pack_moves

            if diff_pack_op and len(pack_pickings) > len(pack_moves):
                for pack in diff_pack_op:
                    if pack.product_qty > 0:
                        # Create po line that is matched with pack which was added manually
                        po_line = picking.prepare_vals_order_line(pack)
                        if po_line:
                            moves = po_line._create_stock_moves(picking)
                            move_ids = moves.action_confirm()
                            moves = self.env['stock.move'].browse(move_ids)
                            seq = 0
                            for move in sorted(
                                    moves, key=lambda move: move.date_expected):
                                seq += 5
                                move.sequence = seq
                            moves.force_assign()
                    else:
                        pack.unlink()
            return super(StockPicking, self).do_new_transfer()

    @api.multi
    def prepare_vals_order_line(self, diff_pack_op):
        '''
            This method prepares vals to build order line when user add
            more pack operation to stock picking manually.
            To make the stock match with PO to create right invoice
        '''
        self.ensure_one()
        po_line_env = self.env['purchase.order.line']
        order = self.env['purchase.order'].search([
            ('name', '=', self.origin)
        ], limit=1)

        if order:
            procurement_uom_po_qty = self.env['product.uom']._compute_qty_obj(
                diff_pack_op.product_id.uom_po_id, diff_pack_op.package_qty,
                diff_pack_op.product_id.uom_po_id)

            seller = diff_pack_op.product_id._select_seller(
                diff_pack_op.product_id,
                partner_id=self.partner_id,
                quantity=procurement_uom_po_qty,
                date=order.date_order and order.date_order[:10],
                uom_id=self.product_id.uom_po_id)

            product_name = seller and seller[0].product_name or\
                diff_pack_op.product_id.name
            product_code = seller and seller[0].product_code or\
                diff_pack_op.product_id.default_code

            name = "%s%s" % (product_code and '[' + product_code + '] ' or '',
                             product_name)

            price_unit = seller and seller[0].base_price or\
                diff_pack_op.product_id.standard_price

            # Prepare value to create the purchase order line that is matched
            vals = {}

            # Add operation_extra_id field to specify this line was build from
            # a pack operation to create right invoice

            vals.update({
                'name': name,
                'product_id': diff_pack_op.product_id.id,
                'product_qty': diff_pack_op.product_qty,
                'product_qty_package': diff_pack_op.product_qty_package,
                'package_qty': diff_pack_op.package_qty,
                'order_id': order.id,
                'product_uom': diff_pack_op.product_uom_id.id,
                'price_unit': price_unit,
                'date_planned': order.date_planned,
                'taxes_id': [(
                        6, 0, [x.id for x in
                               diff_pack_op.product_id.supplier_taxes_id])],
                'operation_extra_id': diff_pack_op.id
            })
            po_line = po_line_env.create(vals)
            return po_line
