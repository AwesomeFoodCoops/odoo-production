##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
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

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    is_quantity_done_editable = fields.Boolean(
        compute='_compute_is_quantity_done_editable')

    @api.multi
    @api.depends('state', 'picking_id', 'product_id')
    def _compute_is_quantity_done_editable(self):
        for move in self:
            if not move.product_id:
                move.is_quantity_done_editable = False
            elif not move.picking_id.immediate_transfer and move.picking_id.state == 'draft':
                move.is_quantity_done_editable = False
            elif move.picking_id.is_locked and move.state in ('done', 'cancel'):
                move.is_quantity_done_editable = False
            # elif move.show_details_visible:
            #    move.is_quantity_done_editable = False
            elif move.show_operations:
                move.is_quantity_done_editable = False
            else:
                move.is_quantity_done_editable = True

    @api.multi
    def unlink(self):
        for move in self:
            if move.state not in ("draft", "cancel"):
                if move.product_uom_qty == 0:
                    move.state = "cancel"
        return super(StockMove, self).unlink()

    vendor_product_code = fields.Char(
        compute="_compute_move_product_code"
    )

    @api.multi
    def _compute_move_product_code(self):
        for pack in self:
            vendor_product_code = ''
            sellers = pack.product_id.seller_ids
            for seller in sellers:
                if seller.name == pack.picking_id.partner_id:
                    vendor_product_code = seller.product_code
            pack.vendor_product_code = vendor_product_code
