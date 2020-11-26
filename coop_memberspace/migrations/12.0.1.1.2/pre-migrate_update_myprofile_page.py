from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    '''
    Update no update = False for coop_memberspace.myprofile
    '''
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        args = [('name', '=', 'coop_memberspace.myprofile'),
                ('arch_db', 'like', 'get_partner_sex_website')]
        view = env['ir.ui.view'].search(args, limit=1)
        if view:
            args = [('module', '=', 'coop_memberspace'),
                    ('name', '=', 'myprofile'),
                    ('noupdate', '=', True)]
            ir_model_data = env['ir.model.data'].search(args, limit=1)
            if ir_model_data:
                ir_model_data.write({'noupdate': False})
