# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class StockChangeProductQty(models.TransientModel):
    _inherit = "stock.change.product.qty"

    product_id = fields.Many2one(
        'product.product', 'Product', required=True, default=False)

    @api.model
    def default_get(self, fields_list):
        res = super(StockChangeProductQty, self).default_get(fields_list)
        context = self._context
        if context.get('active_model') == 'product.template':
            product_ids = self.env['product.product'].search([
                ('product_tmpl_id', '=', context.get('active_id'))
            ])
            if product_ids:
                res['product_id'] = product_ids[0].id
            else:
                raise UserError(_('Found no related product.product with this product.template.'))
        if context.get('active_model') == 'product.product':
            res['product_id'] = context.get('active_id', False)
        return res
