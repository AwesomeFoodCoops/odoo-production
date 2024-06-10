from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        ir_config = env['ir.config_parameter']
        ir_config.set_param(
            'scrap_order.scrap_origin_required', True)
