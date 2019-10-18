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

import pytz
import re
from openerp import models, fields, api, _
from datetime import datetime, timedelta
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError
import unicodedata as udd


WEEK_NUMBERS = [
    (1, 'A'),
    (2, 'B'),
    (3, 'C'),
    (4, 'D')
]

# this variable is used for shift creation. It tells until when we want to
# create the shifts
SHIFT_CREATION_DAYS = 90


class ShiftTemplate(models.Model):
    _name = 'shift.template'
    _description = 'Shift Template'
    _order = 'shift_type_id, start_datetime'

    # Columns section
    name = fields.Char(
        string='Template Name', compute="_compute_template_name", store=True)
    active = fields.Boolean(default=True, track_visibility="onchange")
    shift_ids = fields.One2many(
        'shift.shift', 'shift_template_id', string='Shifts', readonly=True)
    shift_qty = fields.Integer(
        string='Number of shifts', compute='_compute_shift_qty', store=True)
    user_id = fields.Many2one(
        'res.partner', string='Shift Leader')
    user_ids = fields.Many2many(
        'res.partner', 'res_partner_shift_template_rel', 'shift_template_id',
        'partner_id', string='Shift Leaders')
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'shift.shift'))
    shift_type_id = fields.Many2one(
        'shift.type', string='Category', required=True,
        default=lambda self: self._default_shift_type())
    week_number = fields.Selection(
        WEEK_NUMBERS, string='Week', compute="_compute_week_number",
        store=True)
    color = fields.Integer('Kanban Color Index')
    shift_mail_ids = fields.One2many(
        'shift.template.mail', 'shift_template_id', string='Mail Schedule',
        default=lambda self: self._default_shift_mail_ids())
    seats_max = fields.Integer(
        string='Maximum Attendees Number',
        help="""For each shift you can define a maximum registration of
        seats(number of attendees), above this numbers the registrations
        are not accepted.""")
    seats_availability = fields.Selection(
        [('limited', 'Limited'), ('unlimited', 'Unlimited')],
        'Maximum Attendees', required=True, default='unlimited')
    seats_min = fields.Integer(
        string='Minimum Attendees', oldname='register_min',
        help="""For each shift you can define a minimum reserved seats (number
        of attendees), if it does not reach the mentioned registrations the
        shift can not be confirmed (keep 0 to ignore this rule)""")
    seats_reserved = fields.Integer(
        string='Reserved Seats',
        store=True, readonly=True, compute='_compute_seats_template')
    seats_available = fields.Integer(
        string='Available Seats',
        store=True, readonly=True, compute='_compute_seats_template')
    seats_unconfirmed = fields.Integer(
        string='Unconfirmed Seat Reservations',
        store=True, readonly=True, compute='_compute_seats_template')
    seats_used = fields.Integer(
        string='Number of Participants',
        store=True, readonly=True, compute='_compute_seats_template')
    seats_expected = fields.Integer(
        string='Number of Expected Attendees',
        readonly=True, compute='_compute_seats')
    registration_ids = fields.One2many(
        'shift.template.registration', 'shift_template_id', string='Attendees')
    registration_qty = fields.Integer(
        string='Number of Attendees', compute='_compute_registration_qty',
        store=True)
    shift_ticket_ids = fields.One2many(
        'shift.template.ticket', 'shift_template_id', string='Shift Ticket',
        default=lambda rec: rec._default_tickets(), copy=True)
    reply_to = fields.Char(
        'Reply-To Email',
        help="""The email address of the organizer is likely to be put here,
        with the effect to be in the 'Reply-To' of the mails sent automatically
        at shift or registrations confirmation. You can also put the email
        address of your mail gateway if you use one.""")
    address_id = fields.Many2one(
        'res.partner', string='Location',
        default=lambda self: self._default_location_for_shift())
    country_id = fields.Many2one(
        'res.country', 'Country', related='address_id.country_id', store=True)
    description = fields.Html(
        string='Description', oldname='note', translate=True,
        readonly=False,)
    start_datetime = fields.Datetime(
        string='Start Date Time', required=True, help="First date this shift"
        " will be scheduled")
    start_datetime_tz = fields.Datetime(
        string='Start Date Time', compute="_compute_start_datetime_tz",
        store=True)
    end_datetime = fields.Datetime(
        string='End Date Time', required=True, help="End date of the first"
        "  shift")
    end_datetime_tz = fields.Datetime(
        string='End Date Time', compute="_compute_end_datetime_tz", store=True)
    start_date = fields.Date(
        string='Obsolete Start Date', compute='_compute_start_date',
        help="Technical Field. First date this shift will be scheduled",
        store=True)

    start_time = fields.Float(
        string='Obsolete Start Time', compute='_compute_start_time',
        store=True)

    end_time = fields.Float(
        string='Obsolete End Time', compute='_compute_end_time',
        store=True)

    duration = fields.Float(
        string='Duration (hours)', compute='_compute_duration', store=True)

    updated_fields = fields.Char('Updated Fields')
    last_shift_date = fields.Date(
        "Last Scheduled Shift", compute="_compute_last_shift_date")

    # RECURRENCE FIELD
    rrule_type = fields.Selection([
        ('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'),
        ('yearly', 'Year(s)')], 'Recurrency', default='weekly',
        help="Let the shift automatically repeat at that interval")
    recurrency = fields.Boolean(
        'Recurrent', help="Recurrent Meeting", default=True)
    recurrent_id = fields.Integer('Recurrent ID')
    recurrent_id_date = fields.Datetime('Recurrent ID date')
    end_type = fields.Selection([
        ('count', 'Number of repetitions'), ('end_date', 'End date'),
        ('no_end', 'No end')], string='Recurrence Termination',
        default='no_end',)
    interval = fields.Integer(
        'Repeat Every', help="Repeat every (Days/Week/Month/Year)", default=4)
    count = fields.Integer('Repeat', help="Repeat x times")
    mo = fields.Boolean('Mon', compute="_compute_week_day", store=True)
    tu = fields.Boolean('Tue', compute="_compute_week_day", store=True)
    we = fields.Boolean('Wed', compute="_compute_week_day", store=True)
    th = fields.Boolean('Thu', compute="_compute_week_day", store=True)
    fr = fields.Boolean('Fri', compute="_compute_week_day", store=True)
    sa = fields.Boolean('Sat', compute="_compute_week_day", store=True)
    su = fields.Boolean('Sun', compute="_compute_week_day", store=True)
    month_by = fields.Selection([
        ('date', 'Date of month'), ('day', 'Day of month')], 'Option',)
    day = fields.Integer('Date of month')
    week_list = fields.Selection([
        ('MO', 'Monday'), ('TU', 'Tuesday'), ('WE', 'Wednesday'),
        ('TH', 'Thursday'), ('FR', 'Friday'), ('SA', 'Saturday'),
        ('SU', 'Sunday')], 'Weekday')
    byday = fields.Selection([
        ('1', 'First'), ('2', 'Second'), ('3', 'Third'), ('4', 'Fourth'),
        ('5', 'Fifth'), ('-1', 'Last')], 'By day')
    final_date = fields.Date('Repeat Until')  # The last shift of a recurrence
    rrule = fields.Char(
        compute="_compute_rulestring", store=True, string='Recurrent Rule',)

    is_technical = fields.Boolean(default=False)
    is_ftop = fields.Boolean(
        compute='_compute_is_ftop',
        store=True
    )

    @api.model
    def _default_tickets(self):
        try:
            product = self.env.ref('coop_shift.product_product_shift_standard')
            product2 = self.env.ref('coop_shift.product_product_shift_ftop')
            return [
                {
                    'name': _('Standard'),
                    'product_id': product.id,
                    'price': 0,
                },
                {
                    'name': _('FTOP'),
                    'product_id': product2.id,
                    'price': 0,
                }]
        except ValueError:
            return self.env['shift.template.ticket']

    @api.model
    def _default_location_for_shift(self):
        comp_id = self.env['res.company']._company_default_get('shift.shift')
        if comp_id:
            for child in comp_id.partner_id.child_ids:
                if child.type == 'other' and child.default_addess_for_shifts:
                    return child
            return comp_id.partner_id
    # Compute Section

    @api.multi
    @api.depends('shift_type_id')
    def _compute_is_ftop(self):
        for template in self:
            template.is_ftop = template.shift_type_id.is_ftop

    @api.multi
    @api.depends('shift_ids')
    def _compute_shift_qty(self):
        for template in self:
            template.shift_qty = len(template.shift_ids)

    @api.multi
    @api.depends('registration_ids')
    def _compute_registration_qty(self):
        for template in self:
            current_regs = template.registration_ids
            template.registration_qty = len(current_regs)


    @api.multi
    @api.depends('seats_max', 'registration_ids')
    def _compute_seats_template(self):
        """ Determine reserved, available, reserved but unconfirmed and used
        seats. """
        # initialize fields to 0
        for template in self:
            template.seats_unconfirmed = template.seats_reserved =\
                template.seats_used = template.seats_available = 0
        # aggregate registrations by template and by state
        if self.ids:
            state_field = {
                'draft': 'seats_reserved',
                'open': 'seats_reserved',
                'done': 'seats_used',
            }

        # compute seats_available
        for template in self:
            for reg in template.registration_ids.filtered(
                lambda r, states=state_field.keys():
                    r.is_current and r.state in states):
                template[state_field[reg.state]] += 1
            if template.seats_max > 0:
                template.seats_available = template.seats_max - (
                    template.seats_reserved + template.seats_used)
            template.seats_expected = template.seats_unconfirmed +\
                template.seats_reserved + template.seats_used

    @api.multi
    @api.depends(
        'shift_type_id', 'week_number', 'mo', 'tu', 'we', 'th', 'fr', 'sa',
        'su', 'start_time', 'address_id', 'address_id.name')
    def _compute_template_name(self):
        for template in self:
            if template.shift_type_id == template.env.ref(
                    'coop_shift.shift_type'):
                name = ""
            else:
                prefix_name = template.shift_type_id and \
                    template.shift_type_id.prefix_name or ''
                name = prefix_name + ' - ' or ''
            name += template.week_number and (
                WEEK_NUMBERS[template.week_number - 1][1]) or ""
            name += _("Mo") if template.mo else ""
            name += _("Tu") if template.tu else ""
            name += _("We") if template.we else ""
            name += _("Th") if template.th else ""
            name += _("Fr") if template.fr else ""
            name += _("Sa") if template.sa else ""
            name += _("Su") if template.su else ""
            name += " - %02d:%02d" % (
                int(template.start_time),
                int(round((template.start_time - int(template.start_time)) *
                          60)))
            # add 4 letters from the beginning as a shortcode for place.
            if template.company_id and template.address_id:
                if template.address_id.name and \
                        template.address_id.name != template.company_id.name:
                    addr_name = template.address_id.name
                    isa_characters = \
                        "".join([c for c in addr_name if c.isalnum()])
                    str_place = udd.normalize(
                        "NFKD", isa_characters[0:5]).encode("ascii", "ignore")
                    if str_place:
                        name += " - %s" % (str_place)
            template.name = name

    @api.multi
    @api.depends(
        'byday', 'recurrency', 'final_date', 'rrule_type', 'month_by',
        'interval', 'count', 'end_type', 'mo', 'tu', 'we', 'th', 'fr',
        'sa', 'su', 'day', 'week_list')
    def _compute_rulestring(self):
        """
        Gets Recurrence rule string according to value type RECUR of iCalendar
        from the values given.
        @return: dictionary of rrule value.
        """

        for templ in self:
            # read these fields as SUPERUSER because if the record is private a
            # normal search could raise an error
            recurrent_fields = templ._get_recurrent_fields()
            fields = templ.sudo().read(recurrent_fields)[0]
            if fields['end_type'] == 'no_end':
                fields['end_type'] = 'count'
                fields['count'] = 999
            if fields['recurrency']:
                templ.rrule = templ.compute_rule_string(fields)
            else:
                templ.rrule = ''

    @api.multi
    @api.depends('start_datetime_tz')
    def _compute_start_date(self):
        for template in self:
            if template.start_datetime_tz:
                template.start_date = datetime.strptime(
                    template.start_datetime_tz, '%Y-%m-%d %H:%M:%S').strftime(
                    '%Y-%m-%d')

    @api.multi
    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for template in self:
            if template.start_datetime and template.end_datetime:
                start_date_object = datetime.strptime(
                    template.start_datetime, '%Y-%m-%d %H:%M:%S')
                end_date_object = datetime.strptime(
                    template.end_datetime, '%Y-%m-%d %H:%M:%S')
                template.duration = \
                    (end_date_object - start_date_object).seconds / 3600.0

    @api.multi
    @api.depends('start_datetime')
    def _compute_start_datetime_tz(self):
        tz_name = self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise UserError(_(
                "You can not create Shift Template if your timezone is not"
                " defined."))
        for template in self:
            if template.start_datetime:
                start_date_object = datetime.strptime(
                    template.start_datetime, '%Y-%m-%d %H:%M:%S')
                utc_timestamp = pytz.utc.localize(
                    start_date_object, is_dst=False)
                context_tz = pytz.timezone(tz_name)
                start_date_object_tz = utc_timestamp.astimezone(context_tz)
                template.start_datetime_tz = "%s-%02d-%02d %02d:%02d:%02d" % (
                    start_date_object_tz.year,
                    start_date_object_tz.month,
                    start_date_object_tz.day,
                    start_date_object_tz.hour,
                    start_date_object_tz.minute,
                    start_date_object_tz.second,
                )

    @api.multi
    @api.depends('end_datetime')
    def _compute_end_datetime_tz(self):
        tz_name = self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise UserError(_(
                "You can not create Shift Template if your timezone is not"
                " defined."))
        for template in self:
            if template.end_datetime:
                end_date_object = datetime.strptime(
                    template.end_datetime, '%Y-%m-%d %H:%M:%S')
                utc_timestamp = pytz.utc.localize(
                    end_date_object, is_dst=False)
                context_tz = pytz.timezone(tz_name)
                end_date_object_tz = utc_timestamp.astimezone(context_tz)
                template.end_datetime_tz = "%s-%02d-%02d %02d:%02d:%02d" % (
                    end_date_object_tz.year,
                    end_date_object_tz.month,
                    end_date_object_tz.day,
                    end_date_object_tz.hour,
                    end_date_object_tz.minute,
                    end_date_object_tz.second,
                )

    @api.multi
    @api.depends('start_datetime_tz')
    def _compute_start_time(self):
        for template in self:
            if template.start_datetime_tz:
                start_date_object = datetime.strptime(
                    template.start_datetime_tz, '%Y-%m-%d %H:%M:%S')
                template.start_time = (
                    start_date_object.hour +
                    (start_date_object.minute / 60.0))

    @api.multi
    @api.depends('end_datetime_tz')
    def _compute_end_time(self):
        for template in self:
            if template.end_datetime_tz:
                end_date_object = datetime.strptime(
                    template.end_datetime_tz, '%Y-%m-%d %H:%M:%S')
                template.end_time = (
                    end_date_object.hour +
                    (end_date_object.minute / 60.0))

    @api.multi
    @api.depends('start_date')
    def _compute_week_number(self):
        for template in self:
            if not template.start_date:
                template.week_number = False
            else:
                weekA_date = fields.Date.from_string(
                    self.env.ref('coop_shift.config_parameter_weekA').value)
                start_date = fields.Date.from_string(template.start_date)
                template.week_number =\
                    1 + (((start_date - weekA_date).days // 7) % 4)

    @api.multi
    @api.depends('shift_ids')
    def _compute_last_shift_date(self):
        for template in self:
            if template.shift_ids:
                template.last_shift_date = max(
                    shift.date_begin for shift in template.shift_ids)
            else:
                template.last_shift_date = False

    # Constraint Section
    @api.multi
    @api.constrains('start_datetime', 'end_datetime')
    def _check_date(self):
        for template in self:
            if template.start_datetime >= template.end_datetime:
                raise UserError(_(
                    "End datetime should greater than Start Datetime"))

    @api.multi
    @api.constrains('seats_max', 'seats_available')
    def _check_seats_limit(self):
        for templ in self:
            if templ.seats_availability == 'limited' and templ.seats_max and\
                    templ.seats_available < 0:
                raise UserError(_('No more available seats.'))

    # Default Section
    @api.model
    def _default_shift_mail_ids(self):
        return [(0, 0, {
            'interval_unit': 'now',
            'interval_type': 'after_sub',
            'template_id': self.env.ref('coop_shift.shift_subscription')
        })]

    @api.model
    def _default_shift_type(self):
        return self.env.ref('coop_shift.shift_type')

    # On change Section
    @api.depends('start_datetime')
    @api.multi
    def _compute_week_day(self):
        for template in self:
            if template.start_datetime_tz:
                start_date_object_tz = datetime.strptime(
                    template.start_datetime_tz, '%Y-%m-%d %H:%M:%S')
                wd = start_date_object_tz.weekday()
                template.mo = 0
                template.tu = 0
                template.we = 0
                template.th = 0
                template.fr = 0
                template.sa = 0
                template.su = 0
                if wd == 0:
                    template.mo = True
                    template.week_list = "MO"
                elif wd == 1:
                    template.tu = True
                    template.week_list = "TU"
                elif wd == 2:
                    template.we = True
                    template.week_list = "WE"
                elif wd == 3:
                    template.th = True
                    template.week_list = "TH"
                elif wd == 4:
                    template.fr = True
                    template.week_list = "FR"
                elif wd == 5:
                    template.sa = True
                    template.week_list = "SA"
                elif wd == 6:
                    template.su = True
                    template.week_list = "SU"
                template.day = start_date_object_tz.day
                template.byday = "%s" % (
                    (start_date_object_tz.day - 1) // 7 + 1)

    # Overload Section
    @api.multi
    def write(self, vals):
        if 'updated_fields' not in vals.keys() and len(self.shift_ids):
            vals['updated_fields'] = str(vals)

        if 'user_ids' in vals and 'updated_fields' in vals \
                and len(vals.keys()) <= 2:
            self.update_shift(vals)
        elif 'seats_max' in vals:
            self.update_max_seats_related_shifts(vals.get('seats_max'))
            only_update_seats_max = all(
                key in ['seats_max', 'updated_fields']
                for key in vals.keys()
            )
            if only_update_seats_max:
                vals['updated_fields'] = ''

        res = super(ShiftTemplate, self).write(vals)
        updated_fields = vals.get('updated_fields', '')
        if updated_fields.startswith('{'):
            update_wizard_env = self.env['update.shifts.wizard']
            for shift_template in self:
                wizard_obj = update_wizard_env.create({
                    'template_id': shift_template.id,
                    'updated_fields': updated_fields,
                })
                wizard_obj.write({
                    'line_ids': wizard_obj._get_line_ids(shift_template)
                })
                wizard_obj.update_shifts()

        return res

    # Custom Public Section
    @api.multi
    def discard_changes(self):
        return self.write({'updated_fields': ''})

    @api.multi
    def update_max_seats_related_shifts(self, seats_max):
        """
        Update max seats information in related shifts
        """
        for record in self:
            if len(record.shift_ids):
                shifts = record.shift_ids.filtered(
                    lambda s: s.date_end >= fields.Date.context_today(self)
                    and s.state != 'cancel'
                )
                shifts.with_context(tracking_disable=True).write({
                    'seats_max': seats_max
                })
        return True

    @api.multi
    def update_shift(self, vals):
        """
        Update shift directly for changing only shift 
        leader on shift template
        """
        user_ids = vals.get('user_ids', False)
        if user_ids:
            for record in self:
                if len(record.shift_ids):
                    shifts = record.shift_ids.filtered(
                        lambda s: s.date_end >=
                        fields.Date.context_today(self))

                    # update directly to shifts
                    shifts.with_context(
                        tracking_disable=True).write(vals)
                    
                    # remove user_ids from update_fields, 
                    # keep remain values of other fields
                    vals.update({
                        'updated_fields': ''
                    })
        return True

    @api.multi
    def act_template_shift_from_template(self):
        action = self.env.ref('coop_shift.action_shift_view')
        result = action.read()[0]
        shift_ids = sum([template.shift_ids.ids for template in self], [])
        # choose the view_mode accordingly
        if len(shift_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(
                map(str, shift_ids)) + "])]"
        elif len(shift_ids) == 1:
            res = self.env.ref('coop_shift.view_shift_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = shift_ids and shift_ids[0] or False
        result['context'] = unicode({'search_default_upcoming': 1})
        return result

    @api.multi
    def create_shifts_from_template(self, after=False, before=False):
        if not before:
            before = fields.Datetime.to_string(
                datetime.today() + timedelta(days=SHIFT_CREATION_DAYS))
        for template in self:
            after = template.last_shift_date
            rec_dates = template.get_recurrent_dates(
                after=after, before=before)
            for rec_date in rec_dates:
                start_date_object_tz = datetime.strptime(
                    template.start_datetime_tz, '%Y-%m-%d %H:%M:%S')
                date_begin = datetime.strftime(
                    rec_date + timedelta(hours=(start_date_object_tz.hour)) +
                    timedelta(minutes=(start_date_object_tz.minute)),
                    "%Y-%m-%d %H:%M:%S")
                if date_begin.split(" ")[0] <= template.last_shift_date:
                    continue
                end_date_object_tz = datetime.strptime(
                    template.end_datetime_tz, '%Y-%m-%d %H:%M:%S')
                diff_day = end_date_object_tz.day - start_date_object_tz.day
                diff_month = end_date_object_tz.month -\
                    start_date_object_tz.month
                diff_year = end_date_object_tz.year - start_date_object_tz.year
                date_end = datetime.strftime(
                    rec_date + timedelta(hours=(end_date_object_tz.hour)) +
                    timedelta(minutes=(end_date_object_tz.minute)) +
                    relativedelta(days=diff_day) +
                    relativedelta(months=diff_month) +
                    relativedelta(years=diff_year),
                    "%Y-%m-%d %H:%M:%S")
                rec_date = datetime.strftime(rec_date, "%Y-%m-%d")
                vals = {
                    'shift_template_id': template.id,
                    'name': template.name,
                    'user_ids': [(6, 0, template.user_ids.ids)],
                    'company_id': template.company_id.id,
                    'seats_max': template.seats_max,
                    'seats_availability': template.seats_availability,
                    'seats_min': template.seats_min,
                    'date_begin_tz': date_begin,
                    'date_end_tz': date_end,
                    'state': 'draft',
                    'reply_to': template.reply_to,
                    'address_id': template.address_id.id,
                    'description': template.description,
                    'shift_type_id': template.shift_type_id.id,
                    'week_number': template.week_number,
                    'week_list': template.week_list,
                    'shift_ticket_ids': None,
                }
                shift_id = self.env['shift.shift'].create(vals)
                for ticket in template.shift_ticket_ids:
                    vals = {
                        'name': ticket.name,
                        'shift_id': shift_id.id,
                        'product_id': ticket.product_id.id,
                        'price': ticket.price,
                        'deadline': ticket.deadline,
                        'seats_availability': ticket.seats_availability,
                        'seats_max': ticket.seats_max,
                    }
                    if ticket.product_id.shift_type_id.is_ftop:
                        vals['seats_availability'] = 'limited'
                        vals['seats_max'] = 0
                    ticket_id = self.env['shift.ticket'].create(vals)

                    for attendee in ticket.registration_ids:
                        state, strl_id = attendee._get_state(rec_date)
                        if state:
                            vals = {
                                'partner_id': attendee.partner_id.id,
                                'user_ids': [(6, 0, template.user_ids.ids)],
                                'state': state,
                                'email': attendee.email,
                                'phone': attendee.phone,
                                'name': attendee.name,
                                'shift_id': shift_id.id,
                                'shift_ticket_id': ticket_id.id,
                                'tmpl_reg_line_id': strl_id,
                                'template_created': True,
                            }
                            self.env['shift.registration'].with_context(
                                from_shift_template=True).create(vals)

    def compute_rule_string(self, data):
        """
        Compute rule string according to value type RECUR of iCalendar from
        the values given.
        @param self: the object pointer
        @param data: dictionary of freq and interval value
        @return: string containing recurring rule (empty if no rule)
        """
        if data['interval'] and data['interval'] < 0:
            raise UserError(_('interval cannot be negative.'))
        if data['count'] and data['count'] <= 0:
            raise UserError(_('Event recurrence interval cannot be negative.'))

        def get_week_string(freq, data):
            weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
            if freq == 'weekly':
                byday = map(
                    lambda x: x.upper(), filter(
                        lambda x: data.get(x) and x in weekdays, data))
                if byday:
                    return ';BYDAY=' + ','.join(byday)
            return ''

        def get_month_string(freq, data):
            if freq == 'monthly':
                if data.get('month_by') == 'date' and (
                        data.get('day') < 1 or data.get('day') > 31):
                    raise UserError(_(
                        "Please select a proper day of the month."))

                if data.get('month_by') == 'day':  # Eg : 2nd Monday of month
                    return ';BYDAY=' + data.get('byday') + data.get(
                        'week_list')
                elif data.get('month_by') == 'date':  # Eg : 16th of the month
                    return ';BYMONTHDAY=' + str(data.get('day'))
            return ''

        def get_end_date(data):
            if data.get('final_date'):
                data['end_date_new'] = ''.join((re.compile(r'\d')).findall(
                    data.get('final_date'))) + 'T235959Z'
            return (
                data.get('end_type') == 'count' and
                (';COUNT=' + str(data.get('count'))) or ''
            ) +\
                ((
                    data.get('end_date_new') and
                    data.get('end_type') == 'end_date' and
                    (';UNTIL=' + data.get('end_date_new'))) or '')

        freq = data.get('rrule_type', False)  # day/week/month/year
        res = ''
        if freq:
            interval_srting = data.get('interval') and\
                (';INTERVAL=' + str(data.get('interval'))) or ''
            res = 'FREQ=' + freq.upper() + get_week_string(freq, data) +\
                interval_srting + get_end_date(data) +\
                get_month_string(freq, data)
        return res

    @api.model
    def run_shift_creation(self):
        # This method is called by the cron task
        templates = self.env['shift.template'].search([])
        templates.create_shifts_from_template(
            before=fields.Datetime.to_string(
                datetime.today() + timedelta(days=SHIFT_CREATION_DAYS)))

    # Custom Private Section
    @api.model
    def _get_week_number(self, test_date):
        if not test_date:
            return False
        weekA_date = fields.Datetime.from_string(
            self.env.ref('coop_shift.config_parameter_weekA').value)
        week_number = 1 + (((test_date - weekA_date).days // 7) % 4)
        return week_number

    @api.multi
    def get_recurrent_dates(self, after=None, before=None):
        for template in self:
            start = fields.Datetime.from_string(after or template.start_date)
            stop = fields.Datetime.from_string(before or template.final_date)
            delta = (template.week_number - self._get_week_number(start)) % 4
            start += timedelta(weeks=delta)
            return rrule.rrulestr(str(template.rrule), dtstart=start, ignoretz=True).between(
                after=start, before=stop, inc=True)

    def _get_empty_rrule_data(self):
        return {
            'byday': False,
            'recurrency': False,
            'final_date': False,
            'rrule_type': False,
            'month_by': False,
            'interval': 0,
            'count': False,
            'end_type': False,
            'mo': False,
            'tu': False,
            'we': False,
            'th': False,
            'fr': False,
            'sa': False,
            'su': False,
            'day': False,
            'week_list': False
        }

    def _get_recurrent_fields(self):
        return ['byday', 'recurrency', 'final_date', 'rrule_type', 'month_by',
                'interval', 'count', 'end_type', 'mo', 'tu', 'we', 'th', 'fr',
                'sa', 'su', 'day', 'week_list']
