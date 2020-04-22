# Copyright (C) 2020-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, models


class ShiftMailRegistration(models.Model):
    _inherit = 'shift.mail.registration'

    @api.multi
    def execute(self):
        records_to_send_email = self.filtered(
            lambda rec:
            not rec.mail_sent and
            rec.registration_id.state in ['open', 'done']
        )
        records_to_ignore = self - records_to_send_email
        for rec in records_to_send_email:
            shift_holiday = rec.registration_id.shift_id.long_holiday_id \
                or rec.registration_id.shift_id.single_holiday_id
            if (
                shift_holiday
                and shift_holiday.send_email_reminder
                and shift_holiday.reminder_template_id
            ):
                shift_holiday.reminder_template_id.send_mail(
                    rec.registration_id.id)
        if records_to_send_email:
            records_to_send_email.write({'mail_sent': True})
        if records_to_ignore:
            records_to_ignore.write({'mail_ignored': True})
        return super(ShiftMailRegistration, records_to_send_email).execute()
