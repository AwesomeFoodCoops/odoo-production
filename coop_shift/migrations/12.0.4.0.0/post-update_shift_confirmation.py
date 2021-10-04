from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    shift_cron = env.ref('coop_shift.ir_cron_shift_confirmation', False)
    shift_model = env.ref('coop_shift.model_shift_shift', False)
    if shift_cron and shift_model:
        shift_cron.code = 'model.run_shift_confirmation()'
        shift_cron.model_id = shift_model.id
