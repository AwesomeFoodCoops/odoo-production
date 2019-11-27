# -*- coding: utf-8 -*-

from openerp import models, api
from openerp.addons.connector.session import ConnectorSession
from openerp import SUPERUSER_ID


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def update_history(self):
        self.env['product.history'].update_products_history(
                                self.mapped('product_variant_ids').ids)
        return True

    @api.multi
    def calc_history(self):
        products = self.mapped('product_variant_ids')
        products._compute_history('months')
        products._compute_history('weeks')
        products._compute_history('days')
        return True
