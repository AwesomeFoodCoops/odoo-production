##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if self.purchase_id:
            # S#T35388 - Server Error when receiving Order PO18251
            # Stock move is deleted by merging
            todo_moves = self.env["stock.move"]
            for move_line in self.move_lines:
                if not move_line.purchase_line_id:
                    self.prepare_vals_order_line(move_line)
                    todo_moves |= move_line
            if todo_moves:
                todo_moves._action_confirm()
                todo_moves._action_assign()
        return super().button_validate()

    @api.multi
    def prepare_vals_order_line(self, diff_pack_op):
        '''
            This method prepares vals to build order line when user add
            more pack operation to stock picking manually.
            To make the stock match with PO to create right invoice
        '''
        self.ensure_one()
        if self.purchase_id:
            # Create new po line
            po_line = self.env['purchase.order.line'].with_context(
                skip_move_create=True
            ).create({
                'order_id': self.purchase_id.id,
                'product_id': diff_pack_op.product_id.id,
                'product_uom': diff_pack_op.product_uom.id,
                'date_planned': self.purchase_id.date_planned,
                'price_unit': 0.00,
                'product_qty': 0.00,
                'name': '',
            })
            # Trigger correct description and prices from supplier
            po_line.onchange_product_id()
            # Update quantities and other values
            # These fields are overwritten by onchange_product_id, so we set
            # them here
            po_line.write({
                'product_qty': diff_pack_op.quantity_done,
                'product_qty_package': diff_pack_op.product_qty_package,
                'package_qty': diff_pack_op.package_qty,
                'date_planned': self.purchase_id.date_planned,
            })
            # Update price, etc
            po_line._onchange_quantity()
            # Link to move
            diff_pack_op.purchase_line_id = po_line.id
            # Pos comment
            self.purchase_id.message_post(body=_(
                'Purchase items: %s with %s qty. were created from '
                'incoming shipment (%s).') % (
                    diff_pack_op.product_id.display_name,
                    diff_pack_op.package_qty,
                    self.origin,
                )
            )
            return po_line
