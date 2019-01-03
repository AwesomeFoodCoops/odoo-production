# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError, UserError


class ShiftLeave(models.Model):
    _inherit = 'shift.leave'

    is_parental_leave = fields.Boolean()
    is_exceeded_stop_date = fields.Boolean()
    is_warning_start_date = fields.Boolean()
    start_before_birthday = fields.Boolean()
    exempted_until_end = fields.Boolean()
    regular_stop_date = fields.Date()
    expected_birthdate = fields.Date(string='Expected or actual birthdate')
    provided_birth_certificate = fields.Boolean(
        string='Birth Certificate Provided'
    )
    shared_leave = fields.Boolean(string=' Shared Leave')

    shared_partner_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('is_worker_member', '=', True)],
        string='Shared with'
    )

    state = fields.Selection(selection_add=[('not_finished', 'Not finished')])
    forced_member_status = fields.Selection(
        selection=[
            ('exempted', 'Exempted'),
            ('unsubscribed', 'Unsubscribed'),
        ],
        default='',
        compute='_compute_forced_member_status',
        store=True
    )

    @api.constrains('start_date', 'stop_date')
    def _check_date_range(self):
        for leave in self:
            if leave.is_parental_leave:
                start_date = fields.Date.from_string(leave.start_date)
                stop_date = fields.Date.from_string(leave.stop_date)
                day_diff = (stop_date - start_date).days
                if day_diff > 730:
                    raise ValidationError(_("""You cannot propose a parental leave of more than 24 months, even in case of multiple birth."""))

    @api.onchange('type_id')
    def _onchange_type_id(self):
        parental_shift_type = self.env['shift.leave.type'].search([
            ('name', '=', 'Congé Parental')
        ])
        if self.type_id and self.type_id == parental_shift_type:
            self.is_parental_leave = True
        else:
            self.is_parental_leave = False

    @api.onchange('start_date',
                  'expected_birthdate')
    def _onchange_start_date(self):
        if self.is_parental_leave and self.start_date:
            regular_stop_date = \
                fields.Date.from_string(self.start_date) + relativedelta(
                    years=1)

            if self.expected_birthdate:
                expected_birthdate = fields.Date.from_string(
                    self.expected_birthdate)
                today = fields.Date.from_string(fields.Date.today())
                start_date = fields.Date.from_string(self.start_date)
                self.start_before_birthday = start_date < expected_birthdate
                if expected_birthdate >= today:
                    self.provided_birth_certificate = False
                else:
                    self.non_defined_leave = True

                if self.start_before_birthday:
                    self.stop_date = regular_stop_date
                    self.regular_stop_date = regular_stop_date
                else:
                    # Case member has baby before becoming a cooperative
                    # and baby's age have to be smaller than 1 year old
                    # Calculate the baby's age of current partner
                    baby_age = \
                        today.year - expected_birthdate.year - \
                        (
                            (today.month, today.day) <
                            (expected_birthdate.month, expected_birthdate.day)
                        )
                    if not baby_age:
                        self.stop_date = expected_birthdate + relativedelta(
                            years=1)

                if (expected_birthdate - start_date).days > 84 and \
                        not self.provided_birth_certificate:
                    self.is_warning_start_date = True

    @api.onchange('stop_date')
    def _onchange_stop_date(self):
        if self.start_date and self.stop_date and self.is_parental_leave \
                and self.regular_stop_date:
            regular_stop_date = fields.Date.from_string(self.regular_stop_date)
            stop_date = fields.Date.from_string(self.stop_date)
            if stop_date > regular_stop_date:
                self.is_exceeded_stop_date = True

    @api.depends('is_parental_leave', 'provided_birth_certificate')
    def _compute_forced_member_status(self):
        today = fields.Date.today()
        today_dt = fields.Date.from_string(today)
        for leave in self:
            if leave.is_parental_leave and leave.expected_birthdate \
                    and not leave.exempted_until_end:
                expected_birthdate = fields.Date.from_string(
                    leave.expected_birthdate)
                if (today_dt - expected_birthdate).days < 32:
                    # set forced member status to 'exempted' until 32 days
                    # after leave's expected birth date
                    leave.forced_member_status = 'exempted'

                    # If he/she provides birth certificate -> Make him/her
                    # status to 'exempted' until the stop_date
                    if leave.provided_birth_certificate:
                        leave.exempted_until_end = True
                else:
                    # On 33rd day after leave's expected birth date
                    # If he/she still does not provide birth certificate:
                    # + Update forced status of member to unsubscribed
                    # + Set leave state to not_finished
                    # + Abandon his/her leave
                    if not leave.provided_birth_certificate:
                        leave.forced_member_status = 'unsubscribed'
                        leave.state = 'not_finished'
                    else:
                        # Make member status follow the existing rule
                        leave.forced_member_status = ''

    @api.multi
    def revert_stop_date_parental_leave(self):
        self.ensure_one()
        self.stop_date = self.regular_stop_date
        self.is_exceeded_stop_date = False

    @api.multi
    def ok(self):
        self.ensure_one()
        self.is_exceeded_stop_date = False
        self.is_warning_start_date = False

    @api.multi
    def send_validated_parental_leave_email(self):
        """Send validation email when validated shift.leave"""
        # TODO Fill it out
        self.ensure_one()
        validate_parental_leave_email_template = self.env.ref(
            'coop_parental_leave.validate_parental_leave_email')
        non_defined_parental_leave_mail_template = self.env.ref(
            'coop_parental_leave.validate_non_defined_parental_leave_email')
        after_birthdate_parental_leave_mail_template = self.env.ref(
            'coop_parental_leave.validate_parental_leave_email_after_birthdate')

        # Send validate parental leave email
        validate_parental_leave_email_template.send(self.id)

        # Send validate parental non-defined leave email
        if self.non_defined_leave:
            non_defined_parental_leave_mail_template.send(self.id)

        # Send validate parental after birth date leave email
        if not self.start_before_birthday:
            after_birthdate_parental_leave_mail_template.send(self.id)

    @api.model
    def cron_update_member_forced_status(self):
        """Update member forced status based on parental shift.leave" daily"""
        # Update member status when the parental leave begins
        today = fields.Date.today()
        to_update_leaves = self.search([
            ('start_date', '<=', today),
            ('stop_date', '>=', today),
            ('is_parental_leave', '=', True),
            ('start_before_birthday', '=', True),
            ('provided_birth_certificate', '=', False),
        ])
        to_update_leaves._compute_forced_member_status()

    @api.model
    def cron_send_mail_birth_certificate(self):
        """Send mail about birth certificate of parental shift.leave daily"""
        today = fields.Date.today()
        today_dt = fields.Date.from_string(today)
        before_21days = today_dt - relativedelta(days=21)
        before_33days = today_dt - relativedelta(days=33)

        # Send reminder mail to member if 21 days after leave expected
        # birth date and member does not provide birth certificate
        to_send_reminder_mail_leaves = self.search([
            ('is_parental_leave', '=', True),
            ('provide_birth_certificate', '=', False),
            ('expected_birthdate', '=', before_21days),
        ])

        # CPmessage3
        reminder_birth_certificate_mail_template = self.env.ref(
            'coop_parental_leave.reminder_birth_certificate_leave_email')

        for leave in to_send_reminder_mail_leaves:
            # Send reminder email
            reminder_birth_certificate_mail_template.send(leave.id)

        # Send abandoned mail to member if 33 days after leave expected
        # birth date and member does not provide birth certificate
        to_send_abandoned_mail_leaves = self.search([
            ('is_parental_leave', '=', True),
            ('provide_birth_certificate', '=', False),
            ('expected_birthdate', '=', before_33days),
        ])

        # CPmessage2
        abandoned_parental_leave_email_template = self.env.ref(
            'coop_parental_leave.abandoned_parental_leave_email')
        for leave in to_send_abandoned_mail_leaves:
            # Send abandoned email
            abandoned_parental_leave_email_template.send(leave.id)

    @api.model
    def send_mail_reminder_non_defined_leaves(self):
        # Check if there is a mail template
        mail_template = self.env.ref(
            'coop_membership.reminder_end_leave_email')

        if mail_template:
            today = fields.Date.today()
            today_dt = fields.Date.from_string(today)
            forward_15days_dt = today_dt + relativedelta(days=15)
            to_send_parental_leaves = self.search([
                ('is_send_reminder', '=', False),
                ('non_defined_leave', '=', True),
                ('is_parental_leave', '=', True),
                ('stop_date', '<=', forward_15days_dt),
                ('start_date', '<', today_dt),
            ])
            for leave in to_send_parental_leaves:
                mail_template.send(leave.id)
        return super(ShiftLeave, self).send_mail_reminder_non_defined_leaves()
