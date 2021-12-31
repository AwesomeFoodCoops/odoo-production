from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    '''
    Force to update the view coop_memberspace.echange_de_services
    '''
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        to_deactivate = [
            'coop_memberspace.echange_de_services',
            'coop_memberspace.mywork_ftop',
            'coop_memberspace.programmer_un_extra'
        ]
        for view_name in to_deactivate:
            base_view = env.ref(view_name, False)
            args = [
                ('key', '=', view_name),
                ('id', '!=', base_view.id)
            ]
            views = env['ir.ui.view'].search(args)
            views.write({
                'name': view_name + '_obsolete',
                'key': view_name + '_obsolete',
                'active': False
            })
