# -*- coding: utf-8 -*-

from openerp import models, fields


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    active = fields.Boolean(default=True)
