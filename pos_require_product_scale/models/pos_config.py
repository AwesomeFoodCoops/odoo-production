from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    require_product_scale = fields.Boolean(
        string='Require product to weight in POS',
        default=False,
    )
