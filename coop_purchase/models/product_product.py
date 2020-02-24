# -*- coding: utf-8 -*-
from openerp import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    @api.multi
    def toggle_available_in_pos(self):
        for product in self:
            product.available_in_pos = not product.available_in_pos
