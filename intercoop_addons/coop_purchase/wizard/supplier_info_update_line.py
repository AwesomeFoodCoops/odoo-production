# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class SupplierInfoUpdateLine(models.TransientModel):
    _name = 'supplier.info.update.line'

    product_id = fields.Many2one(
        comodel_name='product.product')

    # get from current document fields
    price_unit = fields.Float(digits=dp.get_precision('Product Price'))
    discount = fields.Float()

    # get from product.supplier.info
    supplier_price_unit = fields.Float(
        digits=dp.get_precision('Product Price'))
    supplier_discount = fields.Float()
    price_policy = fields.Selection(
        selection=[('uom', 'per UOM'), ('package', 'Per Package')]
    )

    po_line_id = fields.Many2one(comodel_name='purchase.order.line')
    invoice_line_id = fields.Many2one(comodel_name='account.invoice.line')
    update_id = fields.Many2one(comodel_name='supplier.info.update')
    seller_id = fields.Many2one(comodel_name='product.supplierinfo')
    show_discount = fields.Boolean(
        related='update_id.show_discount', related_sudo=False)
