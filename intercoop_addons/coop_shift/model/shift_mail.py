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

from openerp import api, fields, models, tools
from datetime import datetime
from dateutil.relativedelta import relativedelta


_INTERVALS = {
    'hours': lambda interval: relativedelta(hours=interval),
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
    'now': lambda interval: relativedelta(hours=0),
}


class ShiftMailScheduler(models.Model):
    """ Shift automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on events since Odoo 9. A cron exists
    that periodically checks for mailing to run. """
    _inherit = 'event.mail'
    _name = 'shift.mail'

    event_id = fields.Many2one(required=False)
    shift_id = fields.Many2one(
        'shift.shift', string='Shift', required=True, ondelete='cascade')
    mail_registration_ids = fields.One2many(
        'shift.mail.registration', 'scheduler_id')
    template_id = fields.Many2one(
        'mail.template', string='Email to Send', ondelete='restrict',
        domain=[('model', '=', 'shift.registration')], required=True,
        help="""This field contains the template of the mail that will be
        automatically sent""")

    @api.one
    @api.depends(
        'mail_sent', 'interval_type', 'shift_id.registration_ids',
        'mail_registration_ids')
    def _compute_done(self):
        if self.interval_type in ['before_event', 'after_event']:
            self.done = self.mail_sent
        else:
            self.done = len(self.mail_registration_ids) ==\
                len(self.shift_id.registration_ids) and\
                all(filter(
                    lambda line: line.mail_sent, self.mail_registration_ids))

    @api.one
    @api.depends(
        'shift_id.state', 'shift_id.date_begin', 'interval_type',
        'interval_unit', 'interval_nbr')
    def _compute_scheduled_date(self):
        if self.shift_id.state not in ['confirm', 'done']:
            self.scheduled_date = False
        else:
            if self.interval_type == 'after_sub':
                date, sign = self.shift_id.create_date, 1
            elif self.interval_type == 'before_event':
                date, sign = self.shift_id.date_begin, -1
            else:
                date, sign = self.shift_id.date_end, 1
            self.scheduled_date = datetime.strptime(
                date, tools.DEFAULT_SERVER_DATETIME_FORMAT) +\
                _INTERVALS[self.interval_unit](sign * self.interval_nbr)

    @api.multi
    def execute(self):
        for sm in self:
            if sm.shift_id.shift_type_id.is_ftop:
                continue
            if sm.shift_id.state != 'confirm':
                continue
            if self.interval_type in ['after_sub', 'before_event']:
                # update registration lines
                lines = []
                for registration in filter(lambda item: item not in [
                        mail_reg.registration_id for mail_reg in
                        sm.mail_registration_ids],
                        sm.shift_id.registration_ids):
                    lines.append((0, 0, {'registration_id': registration.id}))
                if lines:
                    sm.write({'mail_registration_ids': lines})
                # execute scheduler on registrations
                today = datetime.strftime(fields.datetime.now(),
                                          tools.DEFAULT_SERVER_DATETIME_FORMAT)

                # filter mails with ignoring conditions.
                sm.mail_registration_ids.filtered(
                    lambda reg: reg.scheduled_date and \
                        reg.scheduled_date <= today and \
                        not reg.mail_ignored
                    ).execute()
            else:
                if not sm.mail_sent:
                    sm.shift_id.mail_attendees(sm.template_id.id)
                    sm.write({'mail_sent': True})
            return True

    @api.model
    def run(self, autocommit=False):
        today = datetime.strftime(fields.datetime.now(),
                                  tools.DEFAULT_SERVER_DATETIME_FORMAT)
        schedulers = self.search([('done', '=', False),
                                  ('scheduled_date', '<=', today)])

        for scheduler in schedulers:
            scheduler.execute()
            if autocommit:
                self.env.cr.commit()
        return True
