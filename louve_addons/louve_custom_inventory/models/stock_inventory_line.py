# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste (julien.weste@akretion.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    product_qty1 = fields.Float(
        'Ground Floor Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_qty2 = fields.Float(
        'Underground Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_qty = fields.Float(
        compute="_compute_product_qty", store=True, readonly=True)

    @api.multi
    @api.depends('product_qty1', 'product_qty2')
    def _compute_product_qty(self):
        for line in self:
            line.product_qty = line.product_qty1 + line.product_qty2
