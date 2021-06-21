from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductMultiBarcode(models.Model):
    _name = "product.multi.barcode"
    _description = 'Product Multi Barcode'
    _rec_name = "barcode"

    product_id = fields.Many2one("product.product", "Product")
    product_tmpl_id = fields.Many2one(
        "product.template", "Template",
        related="product_id.product_tmpl_id",
        inverse="_set_product_tmpl_id")
    barcode = fields.Char(string="Barcode")

    def _set_product_tmpl_id(self):
        for rec in self:
            product = self.env['product.product'].search([
                ('product_tmpl_id', '=', rec.product_tmpl_id.id)
            ], limit=1)
            rec.product_id = product

    @api.multi
    @api.constrains('barcode')
    def _check_barcode_uniq(self):
        for rec in self:
            if not rec.barcode:
                continue
            one = self.env['product.product'].search([
                ('barcode', '=', rec.barcode),
                ('id', '!=', rec.product_id.id)
            ], limit=1)
            if not one:
                another = self.search([
                    ('barcode', '=', rec.barcode),
                    ('id', '!=', rec.id)
                ], limit=1)
                if another:
                    one = another.product_id
            if one:
                raise UserError(_(
                    'Barcode "{}" has been assigned to the product "{}"!'.format(
                        rec.barcode,
                        one.name
                    )))
