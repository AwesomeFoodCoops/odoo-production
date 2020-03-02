from odoo import fields, models


class PosCategory(models.Model):
    _inherit = "pos.category"

    active = fields.Boolean(default=True)
