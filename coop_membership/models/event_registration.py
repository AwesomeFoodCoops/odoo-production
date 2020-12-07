from datetime import datetime, timedelta

from odoo import api, fields, models, _


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    is_discovery_meeting_event = fields.Boolean(
        'Discovery Meeting Event',
        related='event_id.is_discovery_meeting')
    is_send_reminder = fields.Boolean("Send Reminder", default=False)

    @api.multi
    def get_address_meeting(self):
        for record in self:
            event_address_obj = record.event_id.address_id
            street = event_address_obj and event_address_obj.street or ''
            zip_code = event_address_obj and event_address_obj.zip or ''
            city = event_address_obj and event_address_obj.city or ''
            address = u"{} {} {}".format(street, zip_code, city)
            return address

    @api.multi
    def get_email_contact_meeting(self):
        self.ensure_one()
        company = self.partner_id.company_id or self.env.user.company_id
        company_email = company.email_meeting_contact or company.email
        return company_email

    @api.multi
    def get_time_before(self, number):
        for record in self:
            if record.event_id.date_tz:
                record = record.with_context(tz=record.event_id.date_tz)
            date_begin = record.event_id.date_begin
            time_ago = date_begin - timedelta(minutes=number)
            time_ago = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(record, time_ago))
            time = self.convert_meeting_time(time_ago)
            return time.encode('utf-8')

    @api.multi
    def convert_meeting_time(self, time):
        self.ensure_one()
        time = '%sh%s' % \
               (time[11:].split(':')[0], time.split(':')[1])
        return time

    @api.multi
    def convert_weekdays(self, wd):
        self.ensure_one()
        if wd == 0:
            wd = _("Monday")
        elif wd == 1:
            wd = _("Tuesday")
        elif wd == 2:
            wd = _("Wednesday")
        elif wd == 3:
            wd = _("Thursday")
        elif wd == 4:
            wd = _("Friday")
        elif wd == 5:
            wd = _("Saturday")
        elif wd == 6:
            wd = _("Sunday")
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
