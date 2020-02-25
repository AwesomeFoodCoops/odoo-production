from odoo import fields, models


class PurchaseConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    update_main_vendor_on_update_vendor_price = fields.Boolean(
        string='The action "Update Vendors Prices" defines Vendor as Main '
               'Vendor of selected products',
        config_parameter='update_main_vendor_on_update_vendor_price',
    )
