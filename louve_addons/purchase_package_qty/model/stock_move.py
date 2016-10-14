# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
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

from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    package_qty = fields.Float(
        'Package Qty', compute='_compute_package_qty',
        help="""The quantity of products in the supplier package.""")
    indicative_package = fields.Boolean('Indicative Package')
    product_qty_package = fields.Float(
        'Number of packages', help="""The number of packages you'll buy.""")

    # Constraints section
    # TODO: Rewrite me in _contraint, if the Orm V8 allows param in message.

    @api.multi
    @api.depends('product_id')
    def _compute_package_qty(self):
        for pol in self:
            if pol.product_id:
                for supplier in pol.product_id.seller_ids:
                    if pol.partner_id and (supplier.name == pol.partner_id):
                        pol.package_qty = supplier.package_qty

    # Views section
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(StockMove, self).onchange_product_id()
        if self.product_id:
            for supplier in self.product_id.seller_ids:
                if self.partner_id and (supplier.name == self.partner_id):
                    self.package_qty = supplier.package_qty
                    self.product_qty = supplier.package_qty
                    self.product_qty_package = 1
                    self.price_policy = supplier.price_policy
                    self.indicative_package = supplier.indicative_package
        return res

    @api.onchange('product_qty', 'product_uom')
    def onchange_product_qty(self):
        super(StockMove, self)._onchange_quantity()
        res = {}
        if self.package_qty:
            self.product_qty_package = self.product_qty / self.package_qty
        self._compute_amount()
        return res

    @api.onchange('product_qty_package')
    def onchange_product_qty_package(self):
            if self.product_qty_package == int(self.product_qty_package):
                self.product_qty = self.package_qty * self.product_qty_package
