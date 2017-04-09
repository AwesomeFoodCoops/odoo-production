# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class StockChangeProductQty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    product_qty1 = fields.Float(
        'Ground Floor Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_qty2 = fields.Float(
        'Underground Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    current_quantity = fields.Float(
        'Current Quantity', readonly=True,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    new_quantity = fields.Float(
        compute="_compute_new_quantity", store=True, readonly=True)

    @api.multi
    @api.depends('product_qty1', 'product_qty2')
    def _compute_new_quantity(self):
        for wizard in self:
            wizard.new_quantity = wizard.product_qty1 + wizard.product_qty2

    @api.model
    def _prepare_inventory_line(self, inventory_id, data):
        res = super(StockChangeProductQty, self)._prepare_inventory_line(
            inventory_id, data)
        res.update({
            'product_qty1': data['product_qty1'],
            'product_qty2': data['product_qty2'],
        })
        return res

    @api.multi
    def onchange_location_id(self, location_id, product_id):
        """Dispaly Current quantity in a new field"""
        res = super(StockChangeProductQty, self).onchange_location_id(
            location_id, product_id)
        if res.get('value', {}).get('new_quantity', False):
            res['value']['current_quantity'] = res['value']['new_quantity']
            res['value'].pop('new_quantity')
        return res
