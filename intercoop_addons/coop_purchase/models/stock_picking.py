# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        for picking in self:
            for operation in picking.pack_operation_product_ids:
                product = operation.product_id
                if not product.available_in_pos:
                    raise UserError(_('The product {} received should have "available in pos"'.format(product.name)))
        return super(StockPicking, self).do_new_transfer()
