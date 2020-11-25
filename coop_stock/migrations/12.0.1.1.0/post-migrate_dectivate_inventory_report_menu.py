from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        menu = env.ref('stock_account.menu_action_wizard_valuation_history', False)
        if menu:
            menu.active = False
        
        # Clear domain for stock.quantsact
        action = env.ref('stock.quantsact', False)
        if action and action.domain:
            action.domain = False
