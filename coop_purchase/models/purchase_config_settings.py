# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    update_main_vendor_on_update_vendor_price = fields.Boolean(
        string='The action "Update Vendors Prices" defines ' +
        'Vendor as Main Vendor of selected products'
    )

    @api.multi
    def set_default_set_main_vendor_on_update_vendor_price(self):
        print self.ensure_one()
        print self.update_main_vendor_on_update_vendor_price
        self.env['ir.config_parameter'].set_param(
            'update_main_vendor_on_update_vendor_price',
            str(self.update_main_vendor_on_update_vendor_price))

    @api.multi
    def get_default_set_main_vendor_on_update_vendor_price(self):
        value = self.env['ir.config_parameter'].get_param(
            'update_main_vendor_on_update_vendor_price', 'False')

        value = safe_eval(value)

        return {
            'update_main_vendor_on_update_vendor_price': value
        }
