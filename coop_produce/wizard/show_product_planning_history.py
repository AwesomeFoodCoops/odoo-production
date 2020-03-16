
from odoo import api, models, fields, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class PlanificationProductHistory(models.TransientModel):
    _name = "planification.product.history"
    _description = "Product history planning"

    product_id = fields.Many2one('product.product', 'Product', required=True)
    default_packaging = fields.Float(
        'Default packaging',
        related='product_id.default_packaging')
    line_ids = fields.Many2many('order.week.planning.line', string="History")

    @api.model
    def default_get(self, fields):
        context = dict(self._context) or {}
        res = super(PlanificationProductHistory, self).default_get(fields)
        line_ids = context.get('line_ids', [])
        product_id = context.get('product_id', False)
        res.update({
            'product_id': product_id,
            'line_ids': [(6, 0, line_ids)]
        })
        return res

    @api.multi
    def init_display_from_date(self, date):
        raise UserError(_("Not yet implemented"))
