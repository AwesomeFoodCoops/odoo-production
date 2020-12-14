from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    '''
    Update the fr translation for coop_memberspace.myprofile
    '''
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        args = [('module', '=', 'coop_memberspace'),
                ('name', '=', 'myprofile')]
        ir_model_data = env['ir.model.data'].search(args, limit=1)
        if ir_model_data:
            # src: val
            trans_vals = {
                'Activate :': 'Activer',
                'Last name :': 'Nom :',
                'Female': 'Femme',
                'Man': 'Homme'
            }
            lang = 'fr_FR'
            args = [('lang', '=', lang),
                    ('res_id', '=', ir_model_data.res_id),
                    ('name', '=', 'ir.ui.view,arch_db'),
                    ('module', '=', 'coop_memberspace'),
                    ('src', 'in', list(trans_vals.keys()))]
            terms = env['ir.translation'].search(args)
            for t in terms:
                t.value = trans_vals.get(t.src)
