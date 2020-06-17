from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    partner_form = env.ref('coop_shift.view_res_partner_shift_form')
    partner_form.write({'groups_id': [(5, )]})
