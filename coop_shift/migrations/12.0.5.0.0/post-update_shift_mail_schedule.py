from odoo import api, fields, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    today = fields.Datetime.to_string(fields.Datetime.now())
    shifts = env['shift.shift'].search([
        ('date_begin', '>', today),
    ])
    for shift in shifts:
        already_schedules = []
        for schedule in shift.shift_mail_ids:
            already_schedules.append(
                schedule.interval_type.replace('event', 'shift'))
        for shift_mail in shift.shift_template_id.shift_mail_ids:
            if shift_mail.interval_type in already_schedules:
                continue
            vals = {
                'interval_unit': shift_mail.interval_unit,
                'interval_type': shift_mail.interval_type and \
                    shift_mail.interval_type.replace("shift", "event"),
                'interval_nbr': shift_mail.interval_nbr,
                'template_id': shift_mail.template_id.id,
                'shift_id': shift.id
            }
            env['shift.mail'].create(vals)
