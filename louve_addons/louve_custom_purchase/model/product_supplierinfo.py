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

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    @api.multi
    def _get_prices(self):
        for psi in self:
            price_te = price_ti = psi.product_tmpl_id.list_price
            for tax in psi.product_tmpl_id.taxes_id:
                if tax.price_include:
                    price_te = price_te / (1 + tax.amount)
                else:
                    price_ti = price_ti * (1 + tax.amount)
            psi.price_taxes_excluded = price_te
            psi.price_taxes_included = price_ti

    categ_id = fields.Many2one(
        related='product_tmpl_id.categ_id', string='Internal Category',
        store=True)
    default_code = fields.Char(
        related='product_tmpl_id.default_code', string='Internal Reference',
        store=True)
    taxes_id = fields.Many2many(
        related='product_tmpl_id.taxes_id', string='Customer Taxes')
    supplier_taxes_id = fields.Many2many(
        related='product_tmpl_id.supplier_taxes_id', string='Vendor Taxes')
    price_taxes_excluded = fields.Float(
        'Sale Price Taxes Excluded', compute=_get_prices, multi='taxes',
        digits_compute=dp.get_precision('Product Price'),)
    price_taxes_included = fields.Float(
        'Sale Price Taxes Included', compute=_get_prices, multi='taxes',
        digits_compute=dp.get_precision('Product Price'),)

    @api.multi
    @api.depends('price_total', 'product_qty')
    def _compute_price_unit_tax(self):
        for pol in self:
            if pol.product_qty:
                pol.price_unit_tax = pol.price_total / pol.product_qty
