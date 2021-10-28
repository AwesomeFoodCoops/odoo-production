from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    products = env['product.template'].search([
        ('has_theoritical_price_different', '=', True)
    ])
    if products:
        products._compute_has_theoritical_price_different()
