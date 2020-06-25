# Copyright (C) 2020-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, models


class ShiftMailRegistration(models.Model):
    _inherit = 'shift.mail.registration'

    @api.multi
    def execute(self):
        # Records with holidays
        records_with_holiday = self.filtered(
            'registration_id.shift_id.holiday_id')
        records_with_holiday_reminder = records_with_holiday.filtered(
            'registration_id.shift_id.holiday_id.send_email_reminder')
        # We don't send emails here, we just skip them
        records_to_skip = records_with_holiday - records_with_holiday_reminder
        # Records to send holiday reminder
        records_to_send = records_with_holiday_reminder.filtered(
            'registration_id.shift_id.holiday_id.reminder_template_id')
        # Send holiday reminder
        for rec in records_to_send:
            if (
                rec.registration_id.state in ['open', 'done']
                and not rec.mail_sent
            ):
                holiday = rec.registration_id.shift_id.holiday_id
                holiday.reminder_template_id.send_mail(rec.registration_id.id)
                rec.write({'mail_sent': True})
        # We don't process them, they are processed by super()
        records_to_execute = self - records_to_send - records_to_skip
        return super(ShiftMailRegistration, records_to_execute).execute()
