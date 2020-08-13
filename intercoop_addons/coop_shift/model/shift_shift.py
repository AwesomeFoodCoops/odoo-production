# -*- coding: utf-8 -*-
import pytz
from openerp import models, fields, api, _
from openerp.exceptions import UserError
from datetime import datetime, timedelta
from openerp.osv import expression

# this variable is used for shift confirmation. It tells how many days before
# its date_begin a shift is confirmed
SHIFT_CONFIRMATION_DAYS = 5


WEEK_NUMBERS = [
    (1, 'A'),
    (2, 'B'),
    (3, 'C'),
    (4, 'D')
]


class ShiftShift(models.Model):
    _inherit = 'event.event'
    _name = 'shift.shift'
    _description = 'Shift Template'

    @api.model
    def _default_shift_mail_ids(self):
        return [(0, 0, {
            'interval_unit': 'now',
            'interval_type': 'after_sub',
            'template_id': self.env.ref('coop_shift.shift_subscription')
        })]

    name = fields.Char(string="Shift Name")
    event_mail_ids = fields.One2many(default=None)
    shift_mail_ids = fields.One2many(
        'shift.mail', 'shift_id', string='Mail Schedule',
        default=lambda self: self._default_shift_mail_ids())
    shift_type_id = fields.Many2one(
        'shift.type', string='Category', required=False,
        readonly=False, states={'done': [('readonly', True)]})
    week_number = fields.Selection(
        WEEK_NUMBERS, string='Week', compute="_compute_week_number",
        store=True)
    week_list = fields.Selection([
        ('MO', 'Monday'), ('TU', 'Tuesday'), ('WE', 'Wednesday'),
        ('TH', 'Thursday'), ('FR', 'Friday'), ('SA', 'Saturday'),
        ('SU', 'Sunday')], 'Weekday')
    registration_ids = fields.One2many(
        'shift.registration', 'shift_id', string='Attendees',
        readonly=False, states={'done': [('readonly', True)]})
    shift_template_id = fields.Many2one(
        'shift.template', string='Template', ondelete='restrict')
    seats_reserved = fields.Integer(compute='_compute_seats_shift')
    seats_available = fields.Integer(compute='_compute_seats_shift')
    seats_unconfirmed = fields.Integer(compute='_compute_seats_shift')
    seats_used = fields.Integer(compute='_compute_seats_shift')
    seats_expected = fields.Integer(compute='_compute_seats_shift')
    auto_confirm = fields.Boolean(
        string='Confirmation not required', compute='_compute_auto_confirm')
    event_ticket_ids = fields.One2many(
        default=lambda rec: rec._default_tickets())
    shift_ticket_ids = fields.One2many(
        'shift.ticket', 'shift_id', string='Shift Ticket',
        default=lambda rec: rec._default_shift_tickets(), copy=True)
    date_tz = fields.Selection('_tz_get', string='Timezone', default=False)
    date_begin = fields.Datetime(
        compute="_compute_date_begin", store=True, required=False)
    date_begin_tz = fields.Datetime(string='Begin Date Time')
    date_end = fields.Datetime(
        compute="_compute_date_end", store=True, required=False)
    date_end_tz = fields.Datetime(string='End Date Time')
    date_without_time = fields.Date(
        string='Date', compute='_compute_begin_date_fields', store=True,
        multi="begin_date")
    begin_date_string = fields.Char(
        string='Begin Date', compute='_compute_begin_date_fields', store=True,
        multi="begin_date")
    end_date_for_mail = fields.Char(
        string='End Date for mail', compute='_compute_end_date_fields',
        store=True, multi="end_date")
    begin_date_without_time_string = fields.Char(
        string='Begin Date for mail without time', multi="begin_date",
        compute='_compute_begin_date_fields')
    begin_time = fields.Float(
        string='Start Time', compute='_compute_begin_date_fields', store=True,
        multi="begin_date")
    begin_time_string = fields.Char(
        string='Start Time', compute='_compute_begin_date_fields',
        multi="begin_date")
    end_time = fields.Float(
        string='Start Time', compute='_compute_end_date_fields', store=True,
        multi="end_date")
    end_time_for_mail = fields.Char(
        string='End Time', compute='_compute_end_date_fields',
        multi="end_date")
    user_ids = fields.Many2many(
        'res.partner', 'res_partner_shift_shift_rel', 'shift_template_id',
        'partner_id', string='Shift Leaders')
    user_id = fields.Many2one(comodel_name='res.partner', default=False)
    seats_max = fields.Integer()

    _sql_constraints = [(
        'template_date_uniq',
        'unique (shift_template_id, date_begin, company_id)',
        'The same template cannot be planned several time at the same date !'),
    ]

    @api.multi
    @api.depends('date_without_time')
    def _compute_week_number(self):
        for shift in self:
            if not shift.date_without_time:
                shift.week_number = False
            else:
                weekA_date = fields.Date.from_string(
                    self.env.ref('coop_shift.config_parameter_weekA').value)
                start_date = fields.Date.from_string(shift.date_without_time)
                shift.week_number =\
                    1 + (((start_date - weekA_date).days // 7) % 4)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                '|', ('begin_date_string', operator, name),
                ('name', operator, name)
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        shifts = self.search(domain + args, limit=limit)
        return shifts.name_get()

    @api.multi
    @api.depends('name', 'date_begin')
    def name_get(self):
        result = []
        for shift in self:
            name = shift.name + (shift.begin_date_string and
                                 (' ' + shift.begin_date_string) or '')
            result.append((shift.id, name))
        return result

    @api.model
    def _default_tickets(self):
        return None

    @api.model
    def _default_shift_tickets(self):
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
            return self.env['shift.ticket']

    @api.multi
    def _compute_auto_confirm(self):
        for shift in self:
            shift.auto_confirm = False

    @api.model
    def _default_event_mail_ids(self):
        return None

    @api.multi
    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats_shift(self):
        """ Determine reserved, available, reserved but unconfirmed and used
        seats. """
        # initialize fields to 0
        for shift in self:
            shift.seats_unconfirmed = shift.seats_reserved =\
                shift.seats_used = shift.seats_available = 0
        # aggregate registrations by shift and by state
        if self.ids:
            state_field = {
                'draft': 'seats_reserved',
                'open': 'seats_reserved',
                'replacing': 'seats_reserved',
                'done': 'seats_used',
            }
            query = """ SELECT shift_id, state, count(shift_id)
                        FROM shift_registration
                        WHERE shift_id IN %s
                        AND state IN ('draft', 'open', 'done', 'replacing')
                        GROUP BY shift_id, state
                    """
            self._cr.execute(query, (tuple(self.ids),))
            for shift_id, state, num in self._cr.fetchall():
                shift = self.browse(shift_id)
                shift[state_field[state]] += num
        # compute seats_available
        for shift in self:
            if shift.seats_max > 0:
                shift.seats_available = shift.seats_max - (
                    shift.seats_reserved + shift.seats_used)
            shift.seats_expected = shift.seats_unconfirmed +\
                shift.seats_reserved + shift.seats_used

    @api.multi
    def write(self, vals):
        special = self._context.get('special', False)
        if any(shift.state == "done" for shift in self):
            ignore_fields = ['state_in_holiday',
                             'single_holiday_id', 'long_holiday_id']
            for field in vals.keys():
                if field in ignore_fields:
                    break
                raise UserError(_(
                    'You can only repercute changes on draft shifts.'))
        res = super(ShiftShift, self).write(vals)
        if special:
            for field in special:
                if field == 'shift_ticket_ids':
                    for shift in self:
                        template = shift.shift_template_id
                        ftop_ticket = template.shift_ticket_ids.filtered(
                            lambda t: t.shift_type == 'ftop')
                        standard_ticket = template.shift_ticket_ids.filtered(
                            lambda t: t.shift_type == 'standard')
                        ftop_seats_max = ftop_ticket and\
                            ftop_ticket[0].seats_max or False
                        standard_seats_max = standard_ticket and\
                            standard_ticket[0].seats_max or False
                        for ticket in shift.shift_ticket_ids:
                            if ticket.shift_type == 'ftop':
                                ticket.seats_max = ftop_seats_max
                            if ticket.shift_type == 'standard':
                                ticket.seats_max = standard_seats_max
        return res

    @api.onchange('shift_template_id')
    def _onchange_template_id(self):
        if self.shift_template_id:
            self.name = self.shift_template_id.name
            self.user_ids = self.shift_template_id.user_ids
            self.shift_type_id = self.shift_template_id.shift_type_id
            self.week_number = self.shift_template_id.week_number
            cur_date = self.date_begin and datetime.strptime(
                self.date_begin, "%Y-%m-%d %H:%M:%S").date() or\
                datetime.strptime(
                    self.shift_template_id.start_date, "%Y-%m-%d")
            self.date_begin = datetime.strftime(
                cur_date + timedelta(
                    hours=self.shift_template_id.start_time),
                "%Y-%m-%d %H:%M:%S")
            self.date_end = datetime.strftime(
                cur_date + timedelta(
                    hours=self.shift_template_id.end_time),
                "%Y-%m-%d %H:%M:%S")

            cur_attendees = [r.partner_id.id for r in self.registration_ids]
            vals = []
            for attendee in self.shift_template_id.registration_ids:
                if attendee.id not in cur_attendees:
                    vals.append((0, 0, {
                        'partner_id': attendee.id,
                        'state': 'draft',
                        'email': attendee.email,
                        'phone': attendee.phone,
                        'name': attendee.name,
                        'shift_id': self.id,
                    }))
                self.registration_ids = vals

    @api.depends('date_begin_tz')
    @api.multi
    def _compute_date_begin(self):
        tz_name = self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise UserError(_(
                "You can not create Shift if your timezone is not defined."))
        context_tz = pytz.timezone(tz_name)
        for shift in self:
            if shift.date_begin_tz:
                start_date_object_tz = fields.Datetime.from_string(
                    shift.date_begin_tz)
                utc_timestamp = pytz.utc.localize(
                    start_date_object_tz, is_dst=False)
                start_date_object = utc_timestamp.astimezone(context_tz)
                start_date = start_date_object_tz + timedelta(
                    hours=start_date_object_tz.hour - start_date_object.hour)
                shift.date_begin = "%s-%02d-%02d %02d:%02d:%02d" % (
                    start_date.year,
                    start_date.month,
                    start_date.day,
                    start_date.hour,
                    start_date.minute,
                    start_date.second,
                )

    @api.depends('date_end_tz')
    @api.multi
    def _compute_date_end(self):
        tz_name = self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise UserError(_(
                "You can not create Shift if your timezone is not defined."))
        context_tz = pytz.timezone(tz_name)
        for shift in self:
            if shift.date_end_tz:
                end_date_object_tz = fields.Datetime.from_string(
                    shift.date_end_tz)
                utc_timestamp = pytz.utc.localize(
                    end_date_object_tz, is_dst=False)
                end_date_object = utc_timestamp.astimezone(context_tz)
                end_date = end_date_object_tz + timedelta(
                    hours=end_date_object_tz.hour - end_date_object.hour)
                shift.date_end = "%s-%02d-%02d %02d:%02d:%02d" % (
                    end_date.year,
                    end_date.month,
                    end_date.day,
                    end_date.hour,
                    end_date.minute,
                    end_date.second,
                )

    @api.multi
    @api.depends('date_begin_tz')
    def _compute_begin_date_fields(self):
        for shift in self:
            if shift.date_begin_tz:
                start_date_object_tz = datetime.strptime(
                    shift.date_begin_tz, '%Y-%m-%d %H:%M:%S')
                shift.begin_time = (
                    start_date_object_tz.hour +
                    (start_date_object_tz.minute / 60.0))
                shift.begin_time_string = "%02d:%02d" % (
                    start_date_object_tz.hour,
                    start_date_object_tz.minute,
                )
                shift.begin_date_string = "%02d/%02d/%s %02d:%02d" % (
                    start_date_object_tz.day,
                    start_date_object_tz.month,
                    start_date_object_tz.year,
                    start_date_object_tz.hour,
                    start_date_object_tz.minute,
                )
                shift.begin_date_without_time_string = "%02d/%02d/%s" % (
                    start_date_object_tz.day,
                    start_date_object_tz.month,
                    start_date_object_tz.year,
                )
                shift.date_without_time = "%s-%02d-%02d" % (
                    start_date_object_tz.year,
                    start_date_object_tz.month,
                    start_date_object_tz.day,
                )

    @api.multi
    @api.depends('date_end')
    def _compute_end_date_fields(self):
        tz_name = self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise UserError(_(
                "You can not create Shift if your timezone is not defined."))
        for shift in self:
            if shift.date_end:
                shift.end_date_for_mail = datetime.strftime(
                    fields.Datetime.from_string(shift.date_end),
                    "%d/%m/%Y %H:%M")
                shift.end_time_for_mail = datetime.strftime(
                    fields.Datetime.from_string(shift.date_end), "%H:%M")
                start_date_object = datetime.strptime(
                    shift.date_end, '%Y-%m-%d %H:%M:%S')
                utc_timestamp = pytz.utc.localize(
                    start_date_object, is_dst=False)
                context_tz = pytz.timezone(tz_name)
                start_date_object_tz = utc_timestamp.astimezone(context_tz)
                shift.end_time = (
                    start_date_object_tz.hour +
                    (start_date_object_tz.minute / 60.0))

    @api.multi
    def button_confirm(self):
        super(ShiftShift, self).button_confirm()

    @api.model
    def run_shift_confirmation(self):
        # This method is called by the cron task
        compare_date = fields.Date.to_string(
            datetime.today() + timedelta(days=SHIFT_CONFIRMATION_DAYS))
        shifts = self.env['shift.shift'].search([
            ('state', '=', 'draft'),
            ('date_begin', '<=', compare_date)])
        shifts.button_confirm()

    @api.one
    @api.constrains('seats_max', 'seats_available')
    def _check_seats_limit(self):
        return True
