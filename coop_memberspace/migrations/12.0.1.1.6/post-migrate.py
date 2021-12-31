from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    '''
    Force to update the view coop_memberspace.echange_de_services
    '''
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        base_view = env.ref('coop_memberspace.echange_de_services', False)
        args = [
            ('key', '=', 'coop_memberspace.echange_de_services'),
            ('id', '!=', base_view.id)
        ]
        views = env['ir.ui.view'].search(args)
        views.write({
            'name': 'coop_memberspace.echange_de_services_obsolete',
            'key': 'coop_memberspace.echange_de_services_obsolete',
            'active': False
        })
        base_view = env.ref('coop_memberspace.mywork_ftop', False)
        args = [
            ('key', '=', 'coop_memberspace.mywork_ftop'),
            ('id', '!=', base_view.id)
        ]
        views = env['ir.ui.view'].search(args)
        views.write({
            'name': 'coop_memberspace.mywork_ftop_obsolete',
            'key': 'coop_memberspace.mywork_ftop_obsolete',
            'active': False
        })
