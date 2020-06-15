from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    view_id = env.ref('coop_shift.report_timesheet_state')
    if view_id:
        view_id.write({'active': False})
