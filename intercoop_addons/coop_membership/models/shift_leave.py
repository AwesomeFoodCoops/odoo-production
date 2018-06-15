# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz
from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.exceptions import ValidationError


class ShiftLeave(models.Model):
    _inherit = 'shift.leave'

    show_alert_proposed_date = fields.Boolean(
        string='Show Alert Proposed Date', default=False,
        compute='_compute_proposed_date', store=True)
    alert_message = fields.Html(string='Alert Message',
                                compute='_compute_proposed_date',
                                store=True)
    return_date = fields.Date(
        string='Return Date',
        compute='_compute_proposed_date',
        help='Stop Date of the Temporary Leave plus 1 day')
    proposed_date = fields.Date(string='Proposed Date',
                                compute='_compute_proposed_date',
                                store=True)
    shift_date_after_return = fields.Date(
        string="Shift Time after return",
        compute="_compute_shift_time_after_return")
    show_proceed_message = fields.Boolean(
        string='Show Message Proceed', default=False,
        compute='_compute_proceed_message', store=True)
    proceed_message = fields.Html(string='Message Proceed',
                                  compute='_compute_proceed_message',
                                  store=True)
    non_defined_type = fields.Boolean(related="type_id.is_non_defined",
                                      string="Has Non Defined",
                                      store=True)
    non_defined_leave = fields.Boolean(string="Undefined Leave")
    is_send_reminder = fields.Boolean("Send Reminder", default=False)
    event_id = fields.Many2one('shift.counter.event', string="Event Counter")

    @api.multi
    @api.depends('partner_id', 'type_id', 'stop_date', 'non_defined_leave')
    def _compute_proposed_date(self):
        """
        ABCD Member: Proposed Date = Date of the ABCD shift after End Date
            entered - 1
        Volant / FTOP Member:
            Case 1: End Date entered + 7 >= Date of FTOP shift right after
                End Date entered => Proposed Date = Date of FTOP shift right
                after End Date entered + 1
            Case 2: Otherwise, do not propose anything
        """
        for leave in self:
            if leave.type_id.is_temp_leave and leave.non_defined_leave:
                leave.reset_propose_info()
                continue

            if not (leave.partner_id and leave.type_id and leave.stop_date) \
                    or not leave.type_id.is_temp_leave:
                leave.reset_propose_info()
                continue

            stop_date = fields.Date.from_string(leave.stop_date)
            leave.return_date = stop_date + timedelta(days=1)
            partner = leave.partner_id

            leave_stop_time_utc = \
                self.convert_date_to_utc_datetime(
                    leave.stop_date, start_of_day=False)

            next_shift = partner.get_next_shift(
                start_date=leave_stop_time_utc)
            _next_shift_time, next_shift_date = \
                partner.get_next_shift_date(start_date=leave_stop_time_utc)

            if not next_shift_date or not next_shift:
                leave.reset_propose_info()
                continue
            next_shift = next_shift.shift_id

            next_shift_date = fields.Date.from_string(next_shift_date)
            in_ftop_team = partner.in_ftop_team
            if not in_ftop_team and \
                    (next_shift_date + timedelta(days=-1) > stop_date):
                proposed_date = next_shift_date + timedelta(days=-1)
                alert_message = _("You have inputted <b><i>{end_date}</i></b> "
                                  "as the end date of the temporary leave for "
                                  "<b><i>{partner}</i></b>. But a better date"
                                  " would be <b><i>{proposed_date}</i></b> "
                                  "which is one day before the shift "
                                  "<b><i>{shift}</i></b>. Do you accept the "
                                  "proposed date?")
            elif in_ftop_team and \
                    (next_shift_date + timedelta(days=1) <
                     stop_date + timedelta(days=7)):
                proposed_date = next_shift_date + timedelta(days=1)
                alert_message = _("You have inputted <b><i>{end_date}</i>"
                                  "</b> as the end date of the temporary leave"
                                  " for <b><i>{partner}</i></b>. But a better "
                                  "date would be <b><i>{proposed_date}</i></b>"
                                  " which is one day after the shift "
                                  "<b><i>{shift}</i></b>. Do you accept the "
                                  "proposed date?")
            else:
                leave.reset_propose_info()
                continue

            leave.proposed_date = proposed_date

            if leave.proposed_date and leave.proposed_date == leave.stop_date:
                continue

            leave.show_alert_proposed_date = True
            shift_name = next_shift.name + \
                (next_shift.begin_date_string and
                 (' ' + next_shift.begin_date_string) or '')
            leave.alert_message = alert_message.format(
                end_date=stop_date, partner=leave.partner_id.name,
                proposed_date=proposed_date, shift=shift_name)

    @api.multi
    def _compute_shift_time_after_return(self):
        '''
        @Function to get shift time after propose date
        '''
        for leave in self:
            if not leave.partner_id or not leave.return_date:
                leave.shift_date_after_return = False
                continue

            leave_return_time_utc = \
                self.convert_date_to_utc_datetime(leave.return_date)

            # Look for date next shift after return date
            _next_shift_time, next_shift_date = \
                leave.partner_id.get_next_shift_date(
                    start_date=leave_return_time_utc)

            leave.shift_date_after_return = next_shift_date

    @api.multi
    def btn_confirm_propose(self):
        for leave in self:
            leave.show_alert_proposed_date = False
            leave.stop_date = leave.proposed_date

    @api.multi
    def btn_cancel_propose(self):
        for leave in self:
            leave.reset_propose_info()

    def reset_propose_info(self):
        self.proposed_date = False
        self.show_alert_proposed_date = False
        self.alert_message = ''

    def convert_date_to_utc_datetime(self, input_date, start_of_day=True):
        '''
        @Function to convert the date (at 00:00:00) to UTC datetime
        '''
        if start_of_day:
            input_date = input_date + ' 00:00:00'
        else:
            input_date = input_date + ' 23:59:59'

        # Convert input date from string to datetime
        input_date = datetime.strptime(input_date, DTF)

        # Convert to UTC time
        tz_name = self._context.get('tz') or self.env.user.tz
        context_tz = pytz.timezone(tz_name)
        local_dt = context_tz.localize(input_date, is_dst=None)
        return_datetime = local_dt.astimezone(pytz.utc)
        return return_datetime.strftime(DTF)

    @api.multi
    @api.depends('type_id', 'stop_date', 'start_date')
    def _compute_proceed_message(self):
        for leave in self:
            if leave.stop_date and leave.start_date:
                days_leave =\
                    (datetime.strptime(leave.stop_date, "%Y-%m-%d") -
                     datetime.strptime(leave.start_date, "%Y-%m-%d")).days + 1
                if leave.type_id.is_temp_leave and days_leave < 56:
                    leave.show_proceed_message = True
                    leave.proceed_message = (_(
                        "Leave duration is under 8 weeks, do you want to proceed?"
                    ))

    @api.multi
    @api.constrains('type_id', 'partner_id', 'start_date', 'stop_date')
    def _check_leave_for_ABCD_member(self):
        for record in self:
            today = fields.Date.context_today(self)
            abcd_lines_in_leave = record.partner_id.registration_ids.filtered(
                lambda l: l.date_begin >= record.start_date and
                l.date_end <= record.stop_date and l.date_begin >=
                today and l.state != 'cancel' and
                l.shift_ticket_id.shift_type == 'standard')
            if record.type_id.is_anticipated:
                if record.partner_id.in_ftop_team:
                    raise ValidationError(
                        _("This member is not part of an ABCD team."))
                elif record.partner_id.final_standard_point != 0:
                    raise ValidationError(_(
                        "Normally, this member is not eligible for early" +
                        " leave because he has to catch up"))
                elif len(abcd_lines_in_leave) < 2:
                    raise ValidationError(_(
                        "The period of leave must include TWO" +
                        " minimum missed services."))
                elif record.partner_id.final_ftop_point <\
                        len(abcd_lines_in_leave):
                    raise ValidationError(_(
                        "The member does not have enough" +
                        " credits to cover the proposed period."))

    @api.multi
    def update_info_anticipated_leave(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        lines = self.partner_id.registration_ids
        abcd_lines_in_leave = lines.filtered(
            lambda l: l.date_begin >= self.start_date and
            l.date_end <= self.stop_date and l.date_begin >=
            today and l.state != 'cancel' and
            l.shift_ticket_id.shift_type == 'standard')

        # Update FTOP points
        count_point_remove = len(abcd_lines_in_leave)

        point_counter_env = self.env['shift.counter.event']
        event = point_counter_env.sudo().with_context(
            {'automatic': True}).create({
                'name': _('Anticipated Leave'),
                'type': 'ftop',
                'partner_id': self.partner_id.id,
                'point_qty': -count_point_remove,
                'notes': _('This event was created to remove point base' +
                           ' on anticipated leave.')
            })
        self.event_id = event.id

    @api.multi
    def button_cancel(self):
        '''
            Add point counter event base on cancelling leave anticipated
        '''
        super(ShiftLeave, self).button_cancel()
        for leave in self:
            if leave.type_id.is_anticipated and leave.event_id:
                last_notes = leave.event_id.notes
                last_points = leave.event_id.point_qty
                leave.event_id.point_qty = 0
                leave.event_id.notes =\
                    last_notes + '\nLast point quantity: %s' % last_points

    @api.multi
    def update_date_end_anticipated_leave(self, vals):
        partner_id = vals.get('partner_id', self.partner_id.id)
        stop_date = vals.get('stop_date', False)
        partner = self.env['res.partner'].browse(partner_id)
        future_lines = partner.registration_ids.filtered(
            lambda l: l.date_begin >= stop_date)

        # Suggest date end of leave before the registration after leave a day
        if future_lines:
            date_suggest = fields.Date.from_string(
                future_lines[0].date_begin) - timedelta(days=1)
            if stop_date != date_suggest:
                vals.update({
                    'stop_date': date_suggest
                })

    @api.model
    def create(self, vals):
        type_id = vals.get('type_id', False)
        type_leave = self.env['shift.leave.type'].browse(type_id)
        if type_leave.is_anticipated:
            self.update_date_end_anticipated_leave(vals)
        return super(ShiftLeave, self).create(vals)

    @api.multi
    def write(self, vals):
        type_id = vals.get('type_id', self.type_id.id)
        type_leave = self.env['shift.leave.type'].browse(type_id)
        if type_leave.is_anticipated and 'stop_date' in vals:
            self.update_date_end_anticipated_leave(vals)
        return super(ShiftLeave, self).write(vals)

    @api.multi
    def update_registration_template_based_non_define_leave(self):
        '''
        This method is remove such members from their teams 
        immediately by putting the end day for the templates closest the leave
        of current partner. Apply for non-define leave
        '''
        for leave in self:
            if leave.non_defined_type and leave.non_defined_leave:
                # get all template on partner
                template_registration = leave.partner_id.tmpl_reg_line_ids

                # get templates before the stop date leave
                last_templates =\
                    template_registration.filtered(
                        lambda l: l.is_current).sorted(
                        key=lambda l: l.date_begin, reverse=True)
                
                # Must mark leave as done before setting end_date
                # for tmpl_reg_line to make _compute_is_unsubscribed
                # work as expected
                # => (Dont set unsubscribed for this partner in
                # period of non-defined leave)
                leave.state = 'done'

                # put end date to template which has closest begin day and
                # update state leave
                if last_templates:
                    last_templates[0].date_end = fields.Date.from_string(
                        leave.start_date) - timedelta(days=1)
                
        return True

    @api.model
    def send_mail_reminder_non_defined_leaves(self):
        leave_env = self.env['shift.leave']

        leave_to_send = leave_env.search([
            ('is_send_reminder', '=', False),
            ('non_defined_leave', '=', True),
            ('stop_date', '<=',
             (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'))
        ])

        # get mail template and send
        mail_template = self.env.ref(
            'coop_membership.reminder_end_leave_email')
        if mail_template:
            for leave in leave_to_send:
                mail_template.send_mail(leave.id)

            # update sent reminder
            leave_to_send.write({
                'is_send_reminder': True
            })
