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
        return None
        # we temporarily desactivate the default mail
        # return [(0, 0, {
        #     'interval_unit': 'now',
        #     'interval_type': 'after_sub',
        #     'template_id': self.env.ref('coop_shift.shift_subscription')
        # })]

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
    date_without_time = fields.Date(
        string='Date', compute='_compute_begin_date_fields', store=True,
        multi="begin_date")
    begin_date_string = fields.Char(
        string='Begin Date', compute='_compute_begin_date_fields', store=True,
        multi="begin_date")
    begin_time = fields.Float(
        string='Start Time', compute='_compute_begin_time', store=True)
    end_time = fields.Float(
        string='Start Time', compute='_compute_end_time', store=True)
    user_id = fields.Many2one(comodel_name='res.partner', default=False)

    _sql_constraints = [(
        'template_date_uniq',
        'unique (shift_template_id, date_begin, company_id)',
        'The same template cannot be planned several time at the same date !'),
    ]

    @api.depends('date_without_time')
    def _compute_week_number(self):
        if not self.date_without_time:
            self.week_number = False
        else:
            weekA_date = fields.Date.from_string(
                self.env.ref('coop_shift.config_parameter_weekA').value)
            start_date = fields.Date.from_string(self.date_without_time)
            self.week_number = 1 + (((start_date - weekA_date).days // 7) % 4)

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
    @api.constrains('seats_max', 'seats_available')
    def _check_seats_limit(self):
        for shift in self:
            if shift.seats_availability == 'limited' and shift.seats_max and\
                    shift.seats_available < 0:
                raise UserError(_('No more available seats.'))

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
                'draft': 'seats_unconfirmed',
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
        for shift in self:
            if shift.state == "done":
                raise UserError(_(
                    'You can only repercute changes on draft shifts.'))
        return super(ShiftShift, self).write(vals)

    @api.onchange('shift_template_id')
    def _onchange_template_id(self):
        if self.shift_template_id:
            self.name = self.shift_template_id.name
            self.user_id = self.shift_template_id.user_id
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

    @api.multi
    @api.depends('date_begin')
    def _compute_begin_date_fields(self):
        for shift in self:
            shift.date_without_time = datetime.strftime(datetime.strptime(
                shift.date_begin, "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d")
            shift.begin_date_string = datetime.strftime(
                datetime.strptime(shift.date_begin, "%Y-%m-%d %H:%M:%S") +
                timedelta(hours=2), "%d/%m/%Y %H:%M:%S")

    @api.model
    def _convert_time_float(self, t):
        return (((
            float(t.microsecond) / 1000000) + float(t.second) / 60) + float(
            t.minute)) / 60 + t.hour

    @api.multi
    @api.depends('date_begin')
    def _compute_begin_time(self):
        for shift in self:
            shift.begin_time = self._convert_time_float(datetime.strptime(
                shift.date_begin, "%Y-%m-%d %H:%M:%S").time())

    @api.multi
    @api.depends('date_end')
    def _compute_end_time(self):
        for shift in self:
            shift.end_time = self._convert_time_float(datetime.strptime(
                shift.date_end, "%Y-%m-%d %H:%M:%S").time())

    @api.multi
    def confirm_registrations(self):
        for shift in self:
            for ticket in shift.shift_ticket_ids:
                ticket.registration_ids.write(
                    {'state': 'open'})

    @api.model
    def run_shift_confirmation(self):
        # This method is called by the cron task
        compare_date = fields.Date.to_string(
            datetime.today() + timedelta(days=SHIFT_CONFIRMATION_DAYS))
        shifts = self.env['shift.shift'].search([
            ('state', '=', 'draft'),
            ('date_begin', '<=', compare_date)])
        shifts.confirm_registrations()
        shifts.write({'state': 'confirm'})
