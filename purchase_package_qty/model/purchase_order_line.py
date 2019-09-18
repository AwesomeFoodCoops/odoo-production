# -*- coding: utf-8 -*-
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

from math import ceil

from openerp.osv.osv import except_osv
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'price_policy')
    def _compute_amount(self):
        """
        Override native method to compute amount based on price_policy
        (per package or per uom)
        """
        for line in self:
            qty_to_compute = line.product_qty
            if line.price_policy == 'package':
                qty_to_compute = line.product_qty_package
            taxes = line.taxes_id.compute_all(
                line.price_unit, line.order_id.currency_id, qty_to_compute,
                product=line.product_id, partner=line.order_id.partner_id
            )
            line.update({
                'price_tax': taxes['total_included'] - taxes[
                    'total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.model
    def _get_supplierinfovals(self, partner=False):
        if not partner:
            return False
        currency = partner.property_purchase_currency_id or\
            self.env.user.company_id.currency_id
        return {
            'name': partner.id,
            'sequence': max(self.product_id.seller_ids.mapped('sequence')) + 1
            if self.product_id.seller_ids else 1,
            'product_uom': self.product_uom.id,
            'min_qty': 0.0,
            'base_price': self.order_id.currency_id.compute(
                self.price_unit, currency),
            'price_policy': self.price_policy,
            'package_qty': self.package_qty or 1,
            'currency_id': currency.id,
            'delay': 0,
        }

    @api.model
    def _get_package_qty(self):
        if self.product_id and self.partner_id:
            partner = self.partner_id.parent_id or self.partner_id
            if partner in self.product_id.seller_ids.mapped('name'):
                for supplier in self.product_id.seller_ids:
                    if supplier.name == self.partner_id:
                        return supplier.package_qty
        return 1

    @api.model
    def _get_indicative_package(self):
        if self.product_id and self.partner_id:
            partner = self.partner_id.parent_id or self.partner_id
            if partner in self.product_id.seller_ids.mapped('name'):
                for supplier in self.product_id.seller_ids:
                    if supplier.name == self.partner_id:
                        return supplier.indicative_package
        return False

    package_qty = fields.Float(
        'Package Qty', default=lambda self: self._get_package_qty(),
        help="""The quantity of products in the supplier package.""")
    indicative_package = fields.Boolean(
        'Indicative Package',
        default=lambda self: self._get_indicative_package())
    product_qty_package = fields.Float(
        'Number of packages', help="""The number of packages you'll buy.""")
    product_qty = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True, _prefetch=False)       
    price_policy = fields.Selection(
        [('uom', 'per UOM'), ('package', 'per Package')], "Price Policy",
        default='uom', required=True)
    unit_price = fields.Float(
        string='Unit Price', compute="_compute_product_prices",
        digits=dp.get_precision('Product Price'))
    package_price = fields.Float(
        string='Package Price', compute="_compute_product_prices",
        digits=dp.get_precision('Product Price'))

    @api.multi
    @api.depends('package_qty', 'price_unit')
    def _compute_product_prices(self):
        for line in self:
            if line.price_policy == 'package':
                line.unit_price = line.package_qty and\
                    line.price_unit / line.package_qty or 0
                line.package_price = line.price_unit
            else:
                line.unit_price = line.price_unit
                line.package_price = line.price_unit * line.package_qty

    # Constraints section
    # TODO: Rewrite me in _contraint, if the Orm V8 allows param in message.
    @api.one
    @api.constrains('order_id', 'product_id', 'product_qty')
    def _check_purchase_qty(self):
        for pol in self:
            if pol.order_id.state not in ('draft', 'sent'):
                continue
            if not pol.product_id:
                return True
            supplier_id = pol.order_id.partner_id.id
            found = False
            for psi in pol.product_id.seller_ids:
                if psi.name.id == supplier_id:
                    package_qty = psi.package_qty
                    indicative = psi.indicative_package
                    found = True
                    break
            if not found:
                return True
            if not indicative:
                if (int(pol.product_qty / package_qty) !=
                        pol.product_qty / package_qty):
                    raise except_osv(
                        _("Package Error!"),
                        _(
                            """You have to buy a multiple of the package"""
                            """ qty or change the package settings in the"""
                            """ supplierinfo of the product for the"""
                            """ following line:"""
                            """ \n - Product: %s;"""
                            """ \n - Quantity: %s;"""
                            """ \n - Unit Price: %s;"""
                            """ \n - Package quantity: %s;""" % (
                                pol.product_id.name, pol.product_qty,
                                pol.price_unit, package_qty)))

    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)
        self._check_purchase_qty([res])
        return res

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrderLine, self).write(vals)
        self._check_purchase_qty()
        return res

    # Views section
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            for supplier in self.product_id.seller_ids:
                if self.partner_id and (supplier.name == self.partner_id):
                    self.package_qty = supplier.package_qty
                    self.indicative_package = supplier.indicative_package
                    self.product_qty = supplier.package_qty
                    self.product_qty_package = 1
                    self.price_policy = supplier.price_policy
                    break
        return res

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        super(PurchaseOrderLine, self)._onchange_quantity()
        seller = self.product_id._select_seller(
            self.product_id,
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)
        if not seller:
            return
        if seller.price_policy == "package":
            self.price_unit = seller.base_price
        res = {}
        # Use `seller.indicative_package` instead
        # because `self.indicative_package` is still not assigned
        if (not(seller.indicative_package) and self.package_qty > 0 and
                int(self.product_qty / self.package_qty) !=
                self.product_qty / self.package_qty):
            res['warning'] = {
                'title': _('Warning!'),
                'message': _(
                    """The selected supplier only sells """
                    """this product by %s %s""") % (
                    self.package_qty,
                    self.product_uom.name)}
            self.product_qty = ceil(
                self.product_qty / self.package_qty) * self.package_qty
        if self.package_qty:
            self.product_qty_package = self.product_qty / self.package_qty
        self._compute_amount()
        return res

    @api.onchange('product_qty_package')
    def onchange_product_qty_package(self):
        if self.product_qty_package == int(self.product_qty_package):
            product_qty_package = self.product_qty/self.package_qty
            if round(product_qty_package, 2) != self.product_qty_package:
                self.product_qty = self.package_qty * self.product_qty_package

    @api.onchange('package_qty')
    def onchange_package_qty(self):
        if not self.package_qty:
            self.package_qty = 1
        self.product_qty = self.package_qty * self.product_qty_package

    @api.multi
    def _create_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._create_stock_moves(picking)
        for move in res:
            move.package_qty = move.purchase_line_id.package_qty
            move.product_qty_package = \
                move.purchase_line_id.product_qty_package
        return res
