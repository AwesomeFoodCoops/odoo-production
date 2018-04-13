# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz
from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


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

    @api.multi
    @api.depends('partner_id', 'type_id', 'stop_date')
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

            next_shift = partner.get_next_shift(start_date=leave_stop_time_utc)
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
