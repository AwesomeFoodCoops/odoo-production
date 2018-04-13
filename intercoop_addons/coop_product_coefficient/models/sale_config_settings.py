# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    auto_update_base_price = fields.Boolean(
        string='An update of Vendor Price updates Base Price automatically')
    auto_update_theorical_cost = fields.Boolean(
        string='An update of Theorical Cost updates Cost automatically')
    auto_update_theorical_price = fields.Boolean(
        string='An update of Theorical Price updates Price automatically')

    @api.multi
    def get_default_auto_update_price(self):
        # Get default values of Base Price, Theorical Cost, and Theorical Price
        param_env = self.env['ir.config_parameter']
        return {
            'auto_update_base_price':
            safe_eval(param_env.get_param('auto_update_base_price')),
            'auto_update_theorical_cost':
            safe_eval(param_env.get_param('auto_update_theorical_cost')),
            'auto_update_theorical_price':
            safe_eval(param_env.get_param('auto_update_theorical_price')),
        }

    @api.multi
    def set_auto_update_price(self):
        # Set values to Base Price, Theorical Cost, and Theorical Price
        param_env = self.env['ir.config_parameter']
        for rec in self:
            param_env.set_param('auto_update_base_price',
                                rec.auto_update_base_price or 'False')
            param_env.set_param('auto_update_theorical_cost',
                                rec.auto_update_theorical_cost or 'False')
            param_env.set_param('auto_update_theorical_price',
                                rec.auto_update_theorical_price or 'False')
