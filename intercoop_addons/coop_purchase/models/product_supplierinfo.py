# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    is_product_active = fields.Boolean(
        'Active', related="product_tmpl_id.active", store=True)
    product_purchase_ok = fields.Boolean(
        'Product can be purchase', related="product_tmpl_id.purchase_ok",
        store=True)

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
        'Sale Price Taxes Excluded', compute='_get_prices', multi='taxes',
        digits_compute=dp.get_precision('Product Price'), )
    price_taxes_included = fields.Float(
        'Sale Price Taxes Included', compute='_get_prices', multi='taxes',
        digits_compute=dp.get_precision('Product Price'), )

    base_price = fields.Float(
        'Price', required=True,
        digits_compute=dp.get_precision('Product Price'),
        digits=dp.get_precision('Product Price'),
        help="The price to purchase a product"
    )

    @api.multi
    @api.depends('price_total', 'product_qty')
    def _compute_price_unit_tax(self):
        for pol in self:
            if pol.product_qty:
                pol.price_unit_tax = pol.price_total / pol.product_qty

    @api.multi
    def _get_prices(self):
        for psi in self:
            price_te = price_ti = psi.product_tmpl_id.list_price
            for tax in psi.product_tmpl_id.taxes_id:
                if tax.price_include:
                    price_te = price_te / (1 + tax.amount / 100)
                else:
                    price_ti = price_ti * (1 + tax.amount / 100)
            psi.price_taxes_excluded = price_te
            psi.price_taxes_included = price_ti
