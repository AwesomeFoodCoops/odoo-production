
from odoo import models, fields


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    active = fields.Boolean(default=True)
