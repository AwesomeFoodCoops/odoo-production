from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    '''
    Force to update the view coop_memberspace.echange_de_services
    '''
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        res = env['ir.translation'].search([
            ('module', '=', 'coop_memberspace'),
            ('source', '=', 'Inscription'),
            ('value', '=', 'Une inscription')
        ])
        res.unlink()
