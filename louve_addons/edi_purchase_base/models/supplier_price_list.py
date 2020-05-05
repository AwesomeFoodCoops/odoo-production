# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, _


class SupplierPriceList(models.Model):
    _name = 'supplier.price.list'

    import_date = fields.Date(string="Import date", readonly=True)
    supplier_id = fields.Many2one(comodel_name="res.partner", string="EDI Supplier",
                                  domain="[('is_edi', '=', True), ('supplier', '=', True)]", readonly=True,
                                  required=True)
    product_tmpl_id = fields.Many2one(comodel_name="product.template", string="Product", ondelete='set null')
    product_name = fields.Char(string="Product name", readonly=True, required=True)
    supplier_code = fields.Char(string="Supplier code", readonly=True, required=True)
    price = fields.Float('Price', digits_compute=dp.get_precision('Product Price'), readonly=True, required=True,
                         help="The price HT to purchase a product")
    apply_date = fields.Date(string="Apply date", readonly=True, required=True)

    @api.multi
    def button_create_product(self):
        self.ensure_one()
        # create new product
        product_tmpl_id = self.env['product.template'].create({
            'name': self.product_name,
            'sale_ok': True,
            'purchase_ok': True,
            'type': 'product',
            'default_code': self.supplier_code
        })
        # link product with current supplier price list
        self.sudo().product_tmpl_id = product_tmpl_id.id
        # create product supplier info
        self.env['product.supplierinfo'].create({
            'name': self.supplier_id.id,
            'price': self.price,
            'product_code': self.supplier_code,
            'product_tmpl_id': product_tmpl_id.id
        })
        # find similar supplier price list
        supplier_price_list_ids = self.search([
            ('supplier_id', '=', self.supplier_id.id),
            ('product_name', '=', self.product_name),
            ('supplier_code', '=', self.supplier_code),
            ('product_tmpl_id', '=', False)]
        )
        # link product to similar supplier price list
        supplier_price_list_ids.sudo().write({
            'product_tmpl_id': product_tmpl_id.id
        })
        # create action to open newly created product form view
        action = {
            'name': _('Product Form'),
            'view_mode': 'form',
            'res_model': 'product.template',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': product_tmpl_id.id,
        }
        return action
