# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, fields, tools
from datetime import datetime


class ShiftMailRegistration(models.Model):
    _inherit = 'shift.mail.registration'

    @api.one
    def execute(self):
        shift_id = self.registration_id.shift_id
        shift_holiday = shift_id.long_holiday_id or shift_id.single_holiday_id
        if shift_holiday and not shift_holiday.send_email_reminder:
            return
        if shift_holiday and shift_holiday.reminder_template_id:
            if (
                self.registration_id.state in ['open', 'done']
                and not self.mail_sent
            ):
                shift_holiday.reminder_template_id.send_mail(
                    self.registration_id.id)
                self.write({'mail_sent': True})
            return
        return super(ShiftMailRegistration, self).execute()
