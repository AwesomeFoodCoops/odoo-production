# -*- coding: utf-8 -*-
from openerp import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def toggle_available_in_pos(self):
        for rec in self:
            rec.available_in_pos = not rec.available_in_pos
