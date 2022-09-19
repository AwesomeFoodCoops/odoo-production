# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class ShiftHoliday(models.Model):
    _name = "shift.holiday"
    _order = 'date_begin desc'
    _description = 'Shift Holiday'

    HOLIDAY_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ]

    name = fields.Char(string="Name", required=True)
    holiday_type = fields.Selection(
        [('long_period', 'Long Period'), ('single_day', 'Single Day')],
        required=True,
        string=" Holiday Type")
    long_period_shift_ids = fields.One2many(
        'shift.shift', 'long_holiday_id', sring="Shifts")
    single_day_shift_ids = fields.One2many(
        'shift.shift', 'single_holiday_id', string='Shifts')
    date_end = fields.Date(string="Date End", required=True)
    date_begin = fields.Date(string="Date Begin", required=True)
    state = fields.Selection(
        selection=HOLIDAY_STATE_SELECTION, default='draft')
    make_up_type = fields.Selection(
        [('1_make_up', '1 Make Up'), ('0_make_up', '0 Make Up')],
        string="Make Up")
    send_email_reminder = fields.Boolean(
        default=True,
    )
    reminder_template_id = fields.Many2one(
        'mail.template',
        string='Email to Send',
        ondelete='restrict',
        domain=[('model', '=', 'shift.registration')],
        help="""This field contains the template of the mail that will be
            sent instead of Template set in Shift Mail"""
    )

    @api.multi
    @api.constrains('date_begin', 'date_end')
    def check_over_lap(self):
        for record in self:
            if record.date_begin > record.date_end:
                raise ValidationError(
                    _('Date End should be greater than Date Begin.'))
            elif record.holiday_type == 'single_day' and \
                    record.date_end != record.date_begin:
                raise ValidationError(
                    _('Date End should be equal Date Begin in Single Day.'))
            else:
                holidays = self.search([
                    ('date_begin', '<=', record.date_end),
                    ('date_end', '>=', record.date_begin),
                    ('id', '!=', record.id),
                    ('holiday_type', '=', record.holiday_type)
                ])
                if holidays:
                    raise ValidationError(
                        _('There is a holiday already exist in this period'))

    @api.multi
    @api.onchange('holiday_type')
    def onchange_holiday_type(self):
        self.ensure_one()
        if self.holiday_type != 'long_period':
            self.make_up_type = False
            self.send_email_reminder = False
        else:
            self.send_email_reminder = True

    @api.onchange('send_email_reminder')
    def onchange_send_email_reminder(self):
        if not self.send_email_reminder:
            self.reminder_template_id = False

    @api.multi
    def button_confirm(self):
        for record in self:
            shifts = self.env['shift.shift'].search([
                ('date_begin', '>=', record.date_begin),
                ('date_end', '<=', record.date_end),
                ('state', '!=', 'cancel'),
            ])
            # Get shifts base on holiday type ensure that shift weren't
            # on any holiday

            if record.holiday_type == 'long_period':
                shifts = shifts.filtered(lambda s: not s.long_holiday_id)
                record.long_period_shift_ids = [[6, 0, shifts.ids]]
            else:
                shifts = shifts.filtered(lambda s: not s.single_holiday_id)
                record.single_day_shift_ids = [[6, 0, shifts.ids]]
        record.state = 'confirmed'
        return True

    @api.multi
    def button_done(self):
        for record in self:
            if record.holiday_type == 'long_period':
                record.attribute_point_qty_long_period()
            else:
                unmarked_shifts = []
                for shift in record.single_day_shift_ids:
                    if not shift.state_in_holiday:
                        unmarked_shifts.append(shift.name)
                if unmarked_shifts:
                    list_name = '\n- '.join(unmarked_shifts)
                    mess = _(
                        '''Here are shifts that weren't marked open or closed
                                - %s\n
                                Please mark all of shift''') % list_name
                    raise ValidationError(mess)
                else:
                    record.attribute_point_qty_single_day()
            record.state = 'done'
        return True

    @api.multi
    def attribute_point_qty_long_period(self):
        '''
            This method attribute the point qty for attendee on long holiday
            With Rule:
            Plus 2 in holiday type 0 make up with shift type standard and
            attendees was absent
            Plus 1 in holiday type 1 make up for (shift type standard and
            attendees were exscued) or (shift type volant and attendees were
            absent or excused)

        '''
        self.ensure_one()
        point_counter_env = self.env['shift.counter.event']

        # Approve for shift that weren't marked any another single holiday
        shifts = self.long_period_shift_ids.filtered(
            lambda s: not s.single_holiday_id or
            s.single_holiday_id.state != 'done')

        attendees = shifts.mapped('registration_ids')

        for attendee in attendees:
            count_vals = {}
            if self.make_up_type == '0_make_up':
                if not attendee.shift_id.shift_type_id.is_ftop:
                    if attendee.template_created:
                        if attendee.state == 'absent':
                            count_vals = {
                                'point_qty': 2
                            }
                        elif attendee.state == 'excused':
                            count_vals = {
                                'point_qty': 1
                            }
                    elif not attendee.template_created and \
                            attendee.shift_type == 'ftop' and \
                            attendee.state == 'absent':
                        count_vals = {
                            'point_qty': 1
                        }
                elif attendee.shift_id.shift_type_id.is_ftop:
                    if attendee.shift_id.state == 'done':
                        if attendee.partner_id.final_ftop_point >= 0:
                            count_vals = {
                                'point_qty': 1
                            }
                        elif attendee.partner_id.final_ftop_point < -1:
                            if attendee.reduce_extension_id and \
                                    attendee.reduce_extension_id.\
                                    reduce_deduction:
                                count_vals = {
                                    'point_qty': 1
                                }
                            else:
                                count_vals = {
                                    'point_qty': 2
                                }
            else:
                if (not attendee.shift_id.shift_type_id.is_ftop and
                        attendee.state == 'absent' and
                        attendee.template_created) or\
                        (attendee.shift_id.shift_type_id.is_ftop and
                         attendee.shift_id.state == 'done' and
                         attendee.partner_id.final_ftop_point < -1):
                    count_vals = {
                        'point_qty': 1
                    }
            if count_vals:
                count_vals.update({
                    'shift_id': attendee.shift_id.id,
                    'type': attendee.shift_type,
                    'partner_id': attendee.partner_id.id,
                    'name': _('Balance qty for long period holiday'),
                    'holiday_id': self.id,
                })
                point_counter_env.sudo().with_context(
                    automatic=True).create(count_vals)

    @api.multi
    def attribute_point_qty_single_day(self):
        """ This method attribute the point qty for attendees
            are on single holiday With Rule: Plus 2 in shift
            was closed with shift type standard and attendees
            was absent Plus 1 in shift was open for (shift
            type standard and attendees were exscued) or
            (shift type volant and attendees were absent or excused)
        """

        self.ensure_one()
        point_counter_env = self.env['shift.counter.event']

        email_closed_template = self.env.ref(
            'coop_membership.anounce_close_on_holiday_email')
        email_open_template = self.env.ref(
            'coop_membership.anounce_open_on_holiday_email')

        # Reset for overlap (single holiday is preferable than long period)
        another_holiday = self.single_day_shift_ids.filtered(
            lambda s: s.long_holiday_id and
            s.long_holiday_id.state == 'done').mapped('long_holiday_id')

        if another_holiday:
            self.reset_point_qty(another_holiday.ids)

        closed_shifts = self.single_day_shift_ids.filtered(
            lambda s: s.state_in_holiday == 'closed')
        open_shifts = self.single_day_shift_ids.filtered(
            lambda s: s.state_in_holiday == 'open')

        attendee_in_closed_shifts = closed_shifts.mapped('registration_ids')
        attendee_in_open_shifts = open_shifts.mapped('registration_ids')

        # Set maximum available FTOP seats = 0
        ftop_tickets = closed_shifts.mapped('shift_ticket_ids').filtered(
            lambda t: t.shift_type == 'ftop')
        ftop_tickets.write({'seats_max': 0})

        # Balance qty for attendee which are on closed shift
        for attendee_closed in attendee_in_closed_shifts:
            count_vals_closed = {}
            if not attendee_closed.shift_id.shift_type_id.is_ftop:
                if attendee_closed.template_created:
                    if attendee_closed.state == 'absent':
                        count_vals_closed = {
                            'point_qty': 2
                        }
                    elif attendee_closed.state == 'excused':
                        count_vals_closed = {
                            'point_qty': 1
                        }
                elif not attendee_closed.template_created and \
                        attendee_closed.shift_type == 'ftop' and \
                        attendee_closed.state == 'absent':
                    count_vals_closed = {
                        'point_qty': 1
                    }
            elif attendee_closed.shift_id.shift_type_id.is_ftop:
                if attendee_closed.shift_id.state == 'done':
                    if attendee_closed.partner_id.final_ftop_point >= 0:
                        count_vals_closed = {
                            'point_qty': 1
                        }
                    elif attendee_closed.partner_id.final_ftop_point < -1:
                        if attendee_closed.reduce_extension_id and \
                                attendee_closed.reduce_extension_id.\
                                reduce_deduction:
                            count_vals_closed = {
                                'point_qty': 1
                            }
                        else:
                            count_vals_closed = {
                                'point_qty': 2
                            }

            if count_vals_closed:
                count_vals_closed.update({
                    'shift_id': attendee_closed.shift_id.id,
                    'type': attendee_closed.shift_type,
                    'partner_id': attendee_closed.partner_id.id,
                    'name': _('Balance qty for single holiday'),
                    'holiday_id': self.id,
                })
                point_counter_env.sudo().with_context(
                    automatic=True).create(count_vals_closed)

        for attendee_open in attendee_in_open_shifts:
            if (attendee_open.state == 'absent' and
                    attendee_open.template_created and
                    not attendee_open.shift_id.shift_type_id.is_ftop) or \
                    (attendee_open.shift_id.shift_type_id.is_ftop and
                     attendee_open.shift_id.state == 'done' and
                     attendee_open.partner_id.final_ftop_point < -1):
                count_vals_open = {
                    'shift_id': attendee_open.shift_id.id,
                    'type': attendee_open.shift_type,
                    'partner_id': attendee_open.partner_id.id,
                    'point_qty': 1,
                    'name': _('Balance qty for single holiday'),
                    'holiday_id': self.id,
                }
                point_counter_env.sudo().with_context(
                    automatic=True).create(count_vals_open)

        # Send email anounce
        if email_closed_template:
            for attendee_in_closed in attendee_in_closed_shifts:
                if attendee_in_closed.state != 'waiting':
                    email_closed_template.send_mail(attendee_in_closed.id)
        if email_open_template:
            for attdendee_in_open in attendee_in_open_shifts:
                if attdendee_in_open.state != 'waiting':
                    email_open_template.send_mail(attdendee_in_open.id)

    @api.multi
    def reset_point_qty(self, holiday_ids):
        for holiday in self:
            events = self.env['shift.counter.event'].search([
                ('holiday_id', 'in', holiday_ids),
                ('shift_id', 'in', holiday.single_day_shift_ids.ids)])
            for event in events:
                last_qty = event.point_qty
                last_notes = event.notes or ''
                event.point_qty = 0
                event.notes = '%s %s %s' % (
                    last_notes,
                    '\n Point qty was updated by overlap.',
                    '(Last qty is %s)' % (last_qty))
        return True

    @api.multi
    def button_cancel(self):
        for record in self:
            events = record.env['shift.counter.event'].search([
                ('holiday_id', '=', record.id)])

            # Set qty all to 0 for counter event were linked current holiday
            for event in events:
                last_qty = event.point_qty
                last_notes = event.notes or ''
                event.point_qty = 0
                event.notes = '%s %s %s' % (
                    last_notes,
                    '\n Point qty was updated by cancelling holiday.',
                    '(Last qty is %s)' % (last_qty))
            record.state = 'cancel'
        return True

    @api.multi
    def button_draft(self):
        for record in self:
            if record.holiday_type == 'long_period':
                for shift in record.long_period_shift_ids:
                    shift.state_in_holiday = False
                record.long_period_shift_ids = False
            else:
                for shift in record.single_day_shift_ids:
                    shift.state_in_holiday = False
                record.single_day_shift_ids = False
            record.state = 'draft'
        return True

    @api.model
    def cron_update_shifts(self):
        records = self.search([
            ("state", "not in", ("draft", "cancel"))
        ])
        for record in records:
            args = [
                ('date_begin', '>=', record.date_begin),
                ('date_end', '<=', record.date_end),
                ('state', '!=', 'cancel'),
            ]
            if record.holiday_type == 'long_period':
                args.append(("long_holiday_id", "=", False))
            else:
                args.append(("single_holiday_id", "=", False))
            # Get shifts base on holiday type ensure that shift weren't
            # on any holiday
            shifts = self.env['shift.shift'].search(args)
            _logger.info("============================")
            _logger.info("Update shift.holiday for shifts: %s", shifts.ids)
            _logger.info("============================")
            if record.holiday_type == 'long_period':
                shifts.write({"long_holiday_id": record.id})
            else:
                shifts.write({"single_holiday_id": record.id})
