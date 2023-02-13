# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models, fields, api, _, tools
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


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
    barcode = fields.Char(string="Ean")
    price_updated = fields.Boolean()

    @api.multi
    def button_create_product(self):
        self.ensure_one()
        # create new product
        product_tmpl_id = self.env['product.template'].create({
            'name': self.product_name,
            'sale_ok': True,
            'purchase_ok': True,
            'type': 'product',
            'default_code': self.supplier_code,
            'barcode': self.barcode,
        })
        # link product with current supplier price list
        self.sudo().product_tmpl_id = product_tmpl_id.id
        # create product supplier info
        self.env['product.supplierinfo'].create({
            'name': self.supplier_id.id,
            'price': self.price,
            'product_code': self.supplier_code,
            'product_tmpl_id': product_tmpl_id.id,
        })
        self.sudo().price_updated = True
        # find similar supplier price list
        supplier_price_list_ids = self.search([
            ('supplier_id', '=', self.supplier_id.id),
            ('product_name', '=', self.product_name),
            ('supplier_code', '=', self.supplier_code),
            ('product_tmpl_id', '=', False)
        ])
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

    @api.model
    def update_product_price_list(self, product, splists):
        splists = splists.sorted('apply_date')
        splist = splists[-1]
        price = splist.price
        args = [
            ("product_code", "=", splist.supplier_code),
            ("product_tmpl_id", "=", product.id)
        ]
        supplierinfos = self.env["product.supplierinfo"].search(
            args, limit=1)
        if supplierinfos:
            if supplierinfos.base_price != price:
                supplierinfos.base_price = price
        else:
            self.env['product.supplierinfo'].create({
                'name': splist.supplier_id.id,
                'price': price,
                'product_code': splist.supplier_code,
                'product_tmpl_id': product.id,
            })
        splists.sudo().write({"price_updated": True})

    @api.model
    def cron_update_product_price_list(self):
        args = [
            ("product_tmpl_id", "!=", False),
            ("price_updated", "=", False),
            ("supplier_id", "!=", False)
        ]
        recs = self.search(args)
        products = recs.mapped("product_tmpl_id")
        for product in products:
            splists = recs.filtered(lambda r: r.product_tmpl_id == product)
            try:
                self.update_product_price_list(product, splists)
            except Exception as e:
                _logger.error(
                    'Could not update price list for the product %s: %s', product, tools.ustr(e))
