from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    products = env['product.template'].search([])
    products._compute_weight()
    products._compute_price_weight()
    return
