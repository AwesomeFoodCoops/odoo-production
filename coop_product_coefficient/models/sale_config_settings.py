from odoo import fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_update_base_price = fields.Boolean(
        string="An update of Vendor Price updates Base Price automatically",
        config_parameter='coop_product_coefficient.auto_update_base_price'
    )
    auto_update_theorical_cost = fields.Boolean(
        string="An update of Theorical Cost updates Cost automatically",
        config_parameter='coop_product_coefficient.auto_update_theorical_cost'
    )
    auto_update_theorical_price = fields.Boolean(
        string="An update of Theorical Price updates Price automatically",
        config_parameter='coop_product_coefficient.auto_update_theorical_price'
    )
