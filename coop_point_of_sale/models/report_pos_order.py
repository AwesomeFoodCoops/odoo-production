
from odoo import fields, models


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    price_wo_tax = fields.Float(string='Subtotal w/o tax', readonly=True)

    def _select(self):
        res = super()._select()
        res += ', SUM(l.price_subtotal) AS price_wo_tax'
        return res
