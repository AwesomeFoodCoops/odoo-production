# -*- coding: utf-8 -*-

from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_update_prices(self):
        self.ensure_one()
        return self.env.ref('coop_purchase.supplier_info_update_act').read()[0]
