# -*- coding: utf-8 -*-

from openerp import fields, models


class ProductMultiBarcode(models.Model):
    _name = 'product.multi.barcode'
    _rec_name = 'barcode'

    product_id = fields.Many2one('product.product', 'Product')
    barcode = fields.Char(string='Barcode')
