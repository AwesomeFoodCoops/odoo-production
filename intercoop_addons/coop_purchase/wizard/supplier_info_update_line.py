# -*- coding: utf-8 -*-
from openerp import api, fields, models


class SupplierInfoUpdateLine(models.TransientModel):
    _name = 'supplier.info.update.line'

    product_id = fields.Many2one(
        comodel_name='product.product')
    price_unit = fields.Float()
    price_policy = fields.Selection(
        selection=[('uom', 'per UOM'), ('package', 'Per Package')]
    )
    discount = fields.Float()

    po_line_id = fields.Many2one(comodel_name='purchase.order.line')
    invoice_line_id = fields.Many2one(comodel_name='account.invoice.line')
    update_id = fields.Many2one(comodel_name='supplier.info.update')
    seller_id = fields.Many2one(comodel_name='product.supplierinfo')
    show_discount = fields.Boolean(related='update_id.show_discount', related_sudo=False)
