from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    ir_config = env['ir.config_parameter']
    # auto_update_base_price
    auto_update_base_price_old = ir_config.get_param(
        'auto_update_base_price')
    auto_update_base_price = ir_config.get_param(
        'coop_product_coefficient.auto_update_base_price')
    if auto_update_base_price and auto_update_base_price_old:
        cr.execute("""
            DELETE FROM ir_config_parameter
            WHERE key = 'auto_update_base_price'
        """)
    elif not auto_update_base_price and auto_update_base_price_old:
        cr.execute("""
            UPDATE ir_config_parameter
            SET key = 'coop_product_coefficient.auto_update_base_price'
            WHERE key = 'auto_update_base_price'
        """)
    # auto_update_theorical_cost
    auto_update_theorical_cost_old = ir_config.get_param(
        'auto_update_theorical_cost')
    auto_update_theorical_cost = ir_config.get_param(
        'coop_product_coefficient.auto_update_theorical_cost')
    if auto_update_theorical_cost and auto_update_theorical_cost_old:
        cr.execute("""
            DELETE FROM ir_config_parameter
            WHERE key = 'auto_update_theorical_cost'
        """)
    elif not auto_update_theorical_cost and auto_update_theorical_cost_old:
        cr.execute("""
            UPDATE ir_config_parameter
            SET key = 'coop_product_coefficient.auto_update_theorical_cost'
            WHERE key = 'auto_update_theorical_cost'
        """)
    # auto_update_theorical_price
    auto_update_theorical_price_old = ir_config.get_param(
        'auto_update_theorical_price')
    auto_update_theorical_price = ir_config.get_param(
        'coop_product_coefficient.auto_update_theorical_price')
    if auto_update_theorical_price and auto_update_theorical_price_old:
        cr.execute("""
            DELETE FROM ir_config_parameter
            WHERE key = 'auto_update_theorical_price'
         """)
    elif not auto_update_theorical_price and auto_update_theorical_price_old:
        cr.execute("""
            UPDATE ir_config_parameter
            SET key = 'coop_product_coefficient.auto_update_theorical_price'
            WHERE key = 'auto_update_theorical_price'
        """)
