from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    '''
    Update no update = True for coop_memberspace.myprofile
    '''
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        args = [('module', '=', 'coop_memberspace'),
                ('name', '=', 'myprofile'),
                ('noupdate', '=', False)]
        ir_model_data = env['ir.model.data'].search(args, limit=1)
        if ir_model_data:
            ir_model_data.write({'noupdate': True})
