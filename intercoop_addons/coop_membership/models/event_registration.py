# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta


class event_registration(models.Model):
    _inherit = 'event.registration'

    is_discovery_meeting_event = fields.Boolean(
        'Discovery Meeting Event',
        related='event_id.is_discovery_meeting')
    is_send_reminder = fields.Boolean("Send Reminder", default=False)

    @api.multi
    def convert_event_date_begin(self):
        for record in self:
            date = record.event_id.date_begin_located[0:10].split('-')[2] + '/' +\
                record.event_id.date_begin_located[0:10].split('-')[1] + '/' +\
                record.event_id.date_begin_located[0:10].split('-')[0]
            return unicode(date, "utf-8")

    @api.multi
    def get_address_meeting(self):
        for record in self:
            street = record.event_id.address_id and\
                record.event_id.address_id.street or False
            zip_code = record.event_id.address_id and\
                record.event_id.address_id.zip or False
            city = record.event_id.address_id and\
                record.event_id.address_id.city or False
            address = '%s %s %s' % (str(street), str(zip_code), str(city))
            return address

    @api.multi
    def get_email_contact_meeting(self):
        email_contact_meeting =\
            self.env['ir.config_parameter'].sudo().get_param(
                'email_meeting_contact')
        return email_contact_meeting or False

    @api.multi
    def get_time_before(self, number):
        for record in self:
            date_begin = datetime.strptime(record.event_id.date_begin_located,
                                           '%Y-%m-%d %H:%M:%S')
            time_ago = date_begin - timedelta(minutes=number)
            time_ago = fields.Datetime.to_string(time_ago)
            time = self.convert_meeting_time(time_ago)
            return unicode(time, "utf-8")

    @api.multi
    def convert_meeting_time(self, time):
        self.ensure_one()
        time = '%sh%s' %\
            (time[11:].split(':')[0], time.split(':')[1])
        return time

    @api.multi
    def get_time_meeting(self):
        for record in self:
            meeting_time = '%sh%s' %\
                (record.event_id.date_begin_located[11:].split(':')[0],
                 record.event_id.date_begin_located[11:].split(':')[1])
            return meeting_time

    @api.multi
    def get_date_time_meeting(self):
        for record in self:
            date_begin = record.event_id.date_begin_located
            date_end = record.event_id.date_end_located
            wd = datetime.strptime(date_begin, '%Y-%m-%d %H:%M:%S').weekday()
            weekday = self.convert_weekdays(wd)
            month_number = datetime.strptime(date_begin, '%Y-%m-%d %H:%M:%S')
            month = self.convert_month(month_number.month)

            date = date_begin[0:10].split('-')[2]

            meeting_time = self.get_time_meeting()

            time_end = self.convert_meeting_time(date_end)

            date_time_meeting = '%s %s %s de %s à %s' % (
                str(weekday), str(date), str(month), str(meeting_time), str(time_end))

            return unicode(date_time_meeting, "utf-8")

    @api.multi
    def convert_weekdays(self, wd):
        self.ensure_one()
        if wd == 0:
            wd = _("Lundi")
        elif wd == 1:
            wd = _("Mardi")
        elif wd == 2:
            wd = _("Mercredi")
        elif wd == 3:
            wd = _("Jeudi")
        elif wd == 4:
            wd = _("Vendredi")
        elif wd == 5:
            wd = _("Samedi")
        elif wd == 6:
            wd = _("Dimanche")
        return wd

    @api.multi
    def convert_month(self, month):
        self.ensure_one()
        if month == 1:
            month = _("January")
        elif month == 2:
            month = _("February")
        elif month == 3:
            month = _("March")
        elif month == 4:
            month = _("April")
        elif month == 5:
            month = _("May")
        elif month == 6:
            month = _("June")
        elif month == 7:
            month = _("July")
        elif month == 8:
            month = _("August")
        elif month == 9:
            month = _("September")
        elif month == 10:
            month = _("October")
        elif month == 11:
            month = _("November")
        elif month == 12:
            month = _("December")
        return month

    @api.model
    def send_mail_reminder(self):
        registration_env = self.env['event.registration']
        registrations = registration_env.search([
            ('is_send_reminder', '=', False),
            ('state', '=', 'open'),
            ('event_id.date_begin', '>=', fields.Date.context_today(self)),
            ('event_id.date_begin', '<=',
             (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'))
        ])

        # get mail template and send
        mail_template = self.env.ref(
            'coop_membership.registration_reminder_meeting_email')
        if mail_template:
            for registration in registrations:
                mail_template.send_mail(registration.id)

                # update sent reminder
                registration.write({
                    'is_send_reminder': True
                })
        return True
