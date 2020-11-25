from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    '''
    Find and replace "'" by "’" in the translated value from ir.translation
    '''
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        args = [('module', '=', 'coop_memberspace'),
                ('name', '=', 'mail.template,subject'),
                ('type', '=', 'model'),
                ('lang', '=', 'fr_FR'),
                ('value', 'ilike', "'échange")]
        recs = env['ir.translation'].search(args)
        for rec in recs:
            val = rec.value
            val = val.replace("'échange", '’échange')
            rec.value = val
