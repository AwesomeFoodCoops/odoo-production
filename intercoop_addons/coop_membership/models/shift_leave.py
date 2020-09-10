# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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

    is_absence_leave = fields.Boolean()
    medical_excuse_provided = fields.Boolean()
    absence_less_than_15days = fields.Boolean(
        compute='_compute_absence_less_than_15days',
        store=True
    )

    state = fields.Selection(selection_add=[('not_finished', 'Not finished')])

    @api.multi
    @api.constrains('absence_less_than_15days')
    def _check_absence_less_than_15days(self):
        for leave in self:
            if leave.is_absence_leave and leave.absence_less_than_15days:
                raise ValidationError(
                    """Le minimum pour une absence pour incapacité \
                    est de 15 jours.""")

    @api.onchange('type_id')
    def _onchange_type_id_absence(self):
        absence_shift_type = self.env['shift.leave.type'].search([
            ('name', '=', 'Absence pour Incapacité')
        ])
        if self.type_id and self.type_id == absence_shift_type:
            self.is_absence_leave = True
        else:
            self.is_absence_leave = False

    @api.multi
    @api.depends('is_absence_leave', 'duration')
    def _compute_absence_less_than_15days(self):
        for leave in self:
            if leave.is_absence_leave and leave.duration < 15:
                leave.absence_less_than_15days = True
            else:
                leave.absence_less_than_15days = False

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
                next_shift_date = leave.guess_future_date_shift(
                    leave.stop_date, is_all_team=True)
                if next_shift_date:
                    next_shift_date = fields.Date.to_string(
                        next_shift_date[0])
                else:
                    leave.reset_propose_info()
                    continue
            next_shift = next_shift and next_shift.shift_id or ''

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

            date_format =  "%d/%m/%Y"
            leave.show_alert_proposed_date = True
            if next_shift:
                shift_name = next_shift.name + \
                             (next_shift.begin_date_string and
                              (' ' + next_shift.begin_date_string) or '')
            else:
                format_next_shift_date = \
                    next_shift_date and next_shift_date.strftime(date_format) \
                    or ''
                shift_name = ' begin on ' + format_next_shift_date

            format_proposed_date = \
                proposed_date and proposed_date.strftime(date_format) or ''
            format_stop_date = \
                stop_date and stop_date.strftime(date_format) or ''
            leave.alert_message = alert_message.format(
                end_date=format_stop_date, partner=leave.partner_id.name,
                proposed_date=format_proposed_date, shift=shift_name)

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
                        "Leave duration is under 8 weeks, "
                        "do you want to proceed?"))

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
                num_line_guess = \
                    record.calculate_number_shift_future_in_leave()
                total_line = len(abcd_lines_in_leave) + num_line_guess
                if record.partner_id.in_ftop_team:
                    raise ValidationError(_(
                        "This member is not part of an ABCD team."))
                elif record.partner_id.final_standard_point != 0:
                    raise ValidationError(_(
                        "Normally, this member is not eligible for early "
                        "leave because he has to catch up.\n\n"
                        "Count: %d") % record.partner_id.final_standard_point)
                elif total_line < 2:
                    raise ValidationError(_(
                        "The period of leave must include TWO" +
                        " minimum missed services."))
                elif record.partner_id.final_ftop_point < total_line:
                    raise ValidationError(_(
                        "The member does not have enough credits to "
                        "cover the proposed period.\n\n"
                        "Required: %d\n"
                        "Got: %d") % (
                            total_line,
                            record.partner_id.final_ftop_point))

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

        num_shift_guess = self.calculate_number_shift_future_in_leave()

        # Update FTOP points
        count_point_remove = len(abcd_lines_in_leave) + num_shift_guess
        if count_point_remove > self.partner_id.final_ftop_point:
            raise ValidationError(_(
                        "The member does not have enough" +
                        " credits to cover the proposed period."))
        else:
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
    def calculate_number_shift_future_in_leave(self):
        self.ensure_one()
        # Find shift template include current partner
        templates = self.partner_id.tmpl_reg_line_ids.filtered(
            lambda l: (l.is_current or l.is_future) and
            l.shift_ticket_id.shift_type ==
            'standard').mapped('shift_template_id')

        # Get number of shifts in period
        # that is from end date of past ABCD line to the end of leave
        # to guess line partner might register
        num_shift_guess = 0

        for template in templates:
            # last_shift_date is the last day of its shift.shift begin date
            last_shift_date = (fields.Datetime.from_string(
                template.last_shift_date) + timedelta(days=1)).strftime('%Y-%m-%d')

            # Future dates of this template starting from last_shift_date date
            # to leave's stop_date
            rec_dates = template.get_recurrent_dates(
                last_shift_date, self.stop_date)
            for rec in rec_dates:
                date_rec_str = fields.Datetime.to_string(rec)
                if self.start_date < date_rec_str < self.stop_date:
                    num_shift_guess += 1
        return num_shift_guess

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
    def guess_future_date_shift(self, stop_date, is_all_team=False):
        for leave in self:
            templates = leave.partner_id.tmpl_reg_line_ids.filtered(
                lambda l: (l.is_current or l.is_future) and
                l.shift_ticket_id.shift_type ==
                'standard').mapped('shift_template_id')
            if is_all_team and not templates:
                templates = leave.partner_id.tmpl_reg_line_ids.filtered(
                    lambda l: (l.is_current or l.is_future) and
                    l.shift_ticket_id.shift_type ==
                    'ftop').mapped('shift_template_id')
            shift_after_leave = []
            for template in templates:
                # Get the day after end leave 30 days to guess shift after leave
                next_shift_month = (fields.Datetime.from_string(
                    stop_date) + timedelta(days=30)).strftime('%Y-%m-%d')
                rec_dates = template.get_recurrent_dates(
                    stop_date, next_shift_month)

                for rec in rec_dates:
                    if fields.Datetime.to_string(rec) > stop_date:
                        shift_after_leave.append(rec)
            if shift_after_leave:
                shift_after_leave = sorted(shift_after_leave)
            return shift_after_leave

    @api.multi
    def update_date_end_anticipated_leave(self, vals):
        for leave in self:
            partner_id = vals.get('partner_id', leave.partner_id.id)
            stop_date = vals.get('stop_date', False)
            partner = self.env['res.partner'].browse(partner_id)
            future_lines = partner.registration_ids.filtered(
                lambda l: l.date_begin >= stop_date)

            # Suggest date end of leave before the registration after leave a day
            date_shift_guess = leave.guess_future_date_shift(stop_date)
            if date_shift_guess:
                vals.update({
                    'stop_date': fields.Datetime.to_string(
                        date_shift_guess[0] - timedelta(days=1))
                })
            elif future_lines:
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
        res = super(ShiftLeave, self).create(vals)

        if type_leave.is_anticipated:
            partner_id = vals.get('partner_id', self.partner_id.id)
            partner = self.env['res.partner'].browse(partner_id)
            stop_date = vals.get('stop_date', False)

            future_lines = partner.registration_ids.filtered(
                lambda l: l.date_begin >= stop_date)
            date_shift_guess = res.guess_future_date_shift(stop_date)

            if date_shift_guess:
                res.stop_date = fields.Datetime.to_string(
                        date_shift_guess[0] - timedelta(days=1))
            elif future_lines:
                date_suggest = fields.Date.from_string(
                    future_lines[0].date_begin) - timedelta(days=1)
                if stop_date != date_suggest:
                    res.stop_date = date_suggest
        return res

    @api.multi
    def write(self, vals):
        for leave in self:
            type_id = vals.get('type_id', leave.type_id.id)
            type_leave = self.env['shift.leave.type'].browse(type_id)
            if type_leave.is_anticipated and 'stop_date' in vals:
                leave.update_date_end_anticipated_leave(vals)
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
                        key=lambda l: l.date_begin)

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

    @api.multi
    def send_absence_leave_validated_mail(self):
        """Send validation email when validated an absence leave"""
        self.ensure_one()
        confirmation_message_absence_leave_email = self.env.ref(
            'coop_membership.confirmation_message_absence_leave_email')

        # Send validated absence leave email
        if self.is_absence_leave:
            confirmation_message_absence_leave_email.send_mail(self.id)

    @api.model
    def cron_send_mail_absence_leave(self):
        """Send mail about medical_excuse_provided of absence leaves daily"""
        today = fields.Date.today()
        today_dt = fields.Date.from_string(today)
        before_15days = today_dt - relativedelta(days=15)
        before_22days = today_dt - relativedelta(days=22)

        # Send reminder mail to member if 15 days after leave began
        # and medical_excuse_provided wasn't checked
        to_send_reminder_mail_leaves = self.search([
            ('is_absence_leave', '=', True),
            ('medical_excuse_provided', '=', False),
            ('start_date', '=', before_15days),
        ])

        # Reminder Message
        reminder_medical_excuse_mail_template = self.env.ref(
            'coop_membership.reminder_message_absence_leave_email')

        for leave in to_send_reminder_mail_leaves:
            # Send reminder email
            reminder_medical_excuse_mail_template.send_mail(leave.id)

        # Send cancellation mail to member if 22 days after leave began
        # and medical_excuse_provided wasn't checked
        to_send_cancellation_mail_leaves = self.search([
            ('is_absence_leave', '=', True),
            ('medical_excuse_provided', '=', False),
            ('start_date', '=', before_22days),
        ])

        # Cancellation Message
        cancellation_absence_leave_email_template = self.env.ref(
            'coop_membership.cancellation_message_absence_leave_email')
        abandon_absence_leave_email = self.env.ref(
            'coop_membership.abandoned_message_leave_email')

        for leave in to_send_cancellation_mail_leaves:
            leave.state = 'not_finished'
            # Send cancellation email
            cancellation_absence_leave_email_template.send_mail(leave.id)
            abandon_absence_leave_email.send_mail(leave.id)

    @api.model
    def cron_update_shift_leader_end_leave(self):
        """Update shift leaders when leave ends"""
        yesterday_dt = \
            fields.Date.from_string(fields.Date.today()) - timedelta(days=1)
        yesterday_str = fields.Date.to_string(yesterday_dt)
        end_leaves = self.search([
            ('stop_date', '=', yesterday_str)
        ])
        partners = end_leaves.mapped('partner_id')
        for partner in partners:
            partner_leader_templates = self.env['shift.template'].search([
                ('removed_user_ids', 'in', partner.ids)
            ])
            if partner_leader_templates:
                partner_leader_templates.write({
                    'user_ids': [(4, partner.id)],
                    'removed_user_ids': [(3, partner.id)],
                })

