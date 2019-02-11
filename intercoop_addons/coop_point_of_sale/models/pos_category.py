# -*- coding: utf-8 -*-
from openerp import fields, models


class PosCategory(models.Model):
    _inherit = 'pos.category'

    active = fields.Boolean(default=True)
