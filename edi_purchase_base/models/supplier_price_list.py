# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class SupplierPriceList(models.Model):
    _name = "supplier.price.list"
    _description = "Supplier Price List"

    import_date = fields.Date(readonly=True)
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="EDI Supplier",
        domain="[('is_edi', '=', True), ('supplier', '=', True)]",
        readonly=True,
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template", string="Product", ondelete='set null'
    )
    product_name = fields.Char(readonly=True, required=True)
    supplier_code = fields.Char(readonly=True, required=True)
    price = fields.Float(
        digits=dp.get_precision("Product Price"),
        readonly=True,
        required=True,
        help="The price HT to purchase a product",
    )
    apply_date = fields.Date(readonly=True, required=True)

    @api.multi
    def button_create_product(self):
        self.ensure_one()
        # create new product
        product_tmpl_id = self.env['product.template'].create({
            'name': self.product_name,
            'sale_ok': True,
            'purchase_ok': True,
            'type': 'product'
        })
        # link product with current supplier price list
        self.product_tmpl_id = product_tmpl_id.id
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
            ('product_tmpl_id', '=', False)
        ])
        # link product to similar supplier price list
        supplier_price_list_ids.write({'product_tmpl_id': product_tmpl_id.id})
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
