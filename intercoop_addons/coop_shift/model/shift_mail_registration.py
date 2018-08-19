# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, tools
from datetime import datetime


class ShiftMailRegistration(models.Model):
    _inherit = 'event.mail.registration'
    _name = 'shift.mail.registration'

    scheduler_id = fields.Many2one(
        'shift.mail', 'Mail Scheduler', required=True, ondelete='cascade')
    registration_id = fields.Many2one(
        'shift.registration', 'Attendee', required=True, ondelete='cascade')
    mail_ignored = fields.Boolean('Ignored', default=False)

    @api.one
    def execute(self):
        today = datetime.strftime(fields.datetime.now(),
                                  tools.DEFAULT_SERVER_DATETIME_FORMAT)
        # send email for user if shift hasn't started
        if self.registration_id.shift_id.date_begin >= today:
            # when users is in vacation, no email is sent to them.
            if self.registration_id.partner_id.working_state in ['exempted',
                                                                 'vacation']:
                return
            if self.registration_id.shift_id.is_on_holiday:
                return
            return super(ShiftMailRegistration, self).execute()
        else:
            # other case which not sending mail, marked ignore=True
            # they won't be sent ever.
            return self.write({'mail_ignored': True})
