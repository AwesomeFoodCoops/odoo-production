# -*- coding: utf-8 -*-

from openerp import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Make it required only in view to delete purchase orders
    date_planned = fields.Datetime(
        string='Scheduled Date',
        compute='_compute_date_planned',
        required=False,
        store=True,
        index=True,
        oldname='minimum_planned_date'
    )

    @api.multi
    def button_update_prices(self):
        self.ensure_one()
        return self.env.ref('coop_purchase.supplier_info_update_act').read()[0]
