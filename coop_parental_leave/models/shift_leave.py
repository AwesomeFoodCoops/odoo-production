from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ShiftLeave(models.Model):
    _inherit = "shift.leave"

    is_parental_leave = fields.Boolean()
    is_exceeded_stop_date = fields.Boolean()
    is_warning_start_date = fields.Boolean()
    exempted_until_end = fields.Boolean()
    regular_stop_date = fields.Date()
    expected_birthdate = fields.Date(string="Expected or actual birthdate")
    provided_birth_certificate = fields.Boolean(
        string="Birth Certificate Provided"
    )
    shared_leave = fields.Boolean(string=" Shared Leave")
    shared_partner_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_worker_member", "=", True)],
        string="Shared with",
    )
    state = fields.Selection(selection_add=[("not_finished", "Not finished")])
    forced_member_status = fields.Selection(
        selection=[
            ("exempted", "Exempted"),
            ("unsubscribed", "Unsubscribed"),
        ],
        default="",
        compute="_compute_forced_member_status",
        store=True,
    )

    @api.constrains("start_date", "stop_date")
    def _check_date_range(self):
        today = fields.Date.today()
        for leave in self:
            if leave.is_parental_leave:
                day_diff = (leave.stop_date - leave.start_date).days
                if day_diff > 730:
                    raise ValidationError(_(
                        "You cannot propose a parental leave of more "
                        "than 24 months, even in case of multiple birth."
                    ))
                if leave.start_date < leave.expected_birthdate < today:
                    raise ValidationError(_(
                        "You're not allowed to define a parental leave "
                        "in case both expected birth date and "
                        "beginning date are in the past."
                    ))

    @api.onchange("type_id")
    def _onchange_type_id(self):
        parental_shift_type = self.env["shift.leave.type"].search([
            ("name", "=", "Congé Parental")
        ])
        if self.type_id and self.type_id == parental_shift_type:
            self.is_parental_leave = True
        else:
            self.is_parental_leave = False

    @api.onchange("start_date", "expected_birthdate")
    def _onchange_start_date(self):
        today = fields.Date.today()
        if self.is_parental_leave:
            if self.expected_birthdate:
                if self.expected_birthdate >= today:
                    self.provided_birth_certificate = False
            if self.start_date and self.expected_birthdate:
                if self.expected_birthdate >= today:
                    regular_stop_date = self.start_date + relativedelta(
                        years=1
                    ) - relativedelta(days=1)
                    self.regular_stop_date = regular_stop_date
                    self.stop_date = regular_stop_date
                else:
                    # Case member has baby before becoming a cooperative
                    # and baby's age have to be smaller than 1 year old
                    # Calculate the baby's age of current partner
                    baby_age = (today.year - self.expected_birthdate.year - (
                        (today.month, today.day) < (
                            self.expected_birthdate.month,
                            self.expected_birthdate.day
                        )
                    ))
                    if not baby_age:
                        regular_stop_date = self.expected_birthdate + \
                            relativedelta(years=1) - relativedelta(days=1)
                        self.regular_stop_date = regular_stop_date
                        self.stop_date = regular_stop_date
                    else:
                        raise UserError(
                            _(
                                "You are not allowed to have this parental "
                                "leave because of your children's age."
                            )
                        )
                if (self.expected_birthdate - self.start_date).days > 84:
                    self.is_warning_start_date = True
                else:
                    self.is_warning_start_date = False

    @api.onchange("stop_date")
    def _onchange_stop_date(self):
        if self.start_date and self.stop_date and self.is_parental_leave \
                and self.regular_stop_date:
            if self.stop_date > self.regular_stop_date:
                self.is_exceeded_stop_date = True
            else:
                self.is_exceeded_stop_date = False

    @api.depends("is_parental_leave", "provided_birth_certificate")
    def _compute_forced_member_status(self):
        today_dt = fields.Date.today()
        for leave in self:
            if leave.is_parental_leave and leave.expected_birthdate \
                    and not leave.exempted_until_end:
                if (today_dt - leave.expected_birthdate).days <= 32:
                    # set forced member status to 'exempted' until 32 days
                    # after leave's expected birth date
                    leave.forced_member_status = "exempted"
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
                        leave.state = "not_finished"
                        if leave.non_defined_leave:
                            forced_member_status = "unsubscribed"
                        else:
                            forced_member_status = ""
                    else:
                        # Make member status follow the existing rule
                        forced_member_status = ""
                    leave.forced_member_status = forced_member_status

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
        self.ensure_one()
        validate_parental_leave_email_template = self.env.ref(
            "coop_parental_leave.validate_parental_leave_email"
        )
        non_defined_parental_leave_mail_template = self.env.ref(
            "coop_parental_leave.validate_non_defined_parental_leave_email"
        )
        after_birthdate_parental_leave_mail_template = self.env.ref(
            "coop_parental_leave.validate_parental_leave_email_after_birthdate"
        )
        if self.is_parental_leave:
            # Send validate parental leave email
            validate_parental_leave_email_template.send_mail(self.id)
            # Send validate parental non-defined leave email
            if self.non_defined_leave:
                non_defined_parental_leave_mail_template.send_mail(self.id)
            # Send validate parental after birth date leave email
            today_dt = fields.Date.today()
            if self.expected_birthdate < self.start_date \
                    and self.expected_birthdate < today_dt:
                after_birthdate_parental_leave_mail_template.send_mail(self.id)

    @api.model
    def cron_update_member_forced_status(self):
        """Update member forced status based on parental shift.leave" daily"""
        # Update member status when the parental leave begins
        today = fields.Date.today()
        to_update_leaves = self.search([
            ("start_date", "<=", today),
            ("stop_date", ">=", today),
            ("is_parental_leave", "=", True),
            ("provided_birth_certificate", "=", False)
        ])
        to_update_leaves._compute_forced_member_status()

    @api.model
    def cron_send_mail_birth_certificate(self):
        """Send mail about birth certificate of parental shift.leave daily"""
        today_dt = fields.Date.today()
        before_21days = today_dt - relativedelta(days=21)
        before_33days = today_dt - relativedelta(days=33)
        # Send reminder mail to member if 21 days after leave expected
        # birth date and member does not provide birth certificate
        to_send_reminder_mail_leaves = self.search([
            ("is_parental_leave", "=", True),
            ("provided_birth_certificate", "=", False),
            ("expected_birthdate", "=", before_21days)
        ])
        # CPmessage3
        reminder_birth_certificate_mail_template = self.env.ref(
            "coop_parental_leave.reminder_birth_certificate_leave_email"
        )
        for leave in to_send_reminder_mail_leaves:
            # Send reminder email
            reminder_birth_certificate_mail_template.send_mail(leave.id)
        # Send abandoned mail to member if 33 days after leave expected
        # birth date and member does not provide birth certificate
        to_send_abandoned_mail_leaves = self.search([
            ("is_parental_leave", "=", True),
            ("provided_birth_certificate", "=", False),
            ("expected_birthdate", "=", before_33days),
        ])
        # CPmessage2
        abandoned_parental_leave_email_template = self.env.ref(
            "coop_parental_leave.abandoned_parental_leave_email"
        )
        for leave in to_send_abandoned_mail_leaves:
            # Send abandoned email
            abandoned_parental_leave_email_template.send_mail(leave.id)

    @api.model
    def send_mail_reminder_non_defined_leaves(self):
        # Check if there is a mail template
        mail_template = self.env.ref(
            "coop_membership.reminder_end_leave_email"
        )
        if mail_template:
            today_dt = fields.Date.today()
            forward_15days_dt = today_dt + relativedelta(days=15)
            to_send_parental_leaves = self.search([
                ("is_send_reminder", "=", False),
                ("non_defined_leave", "=", True),
                ("is_parental_leave", "=", True),
                ("stop_date", "<=", forward_15days_dt),
                ("start_date", "<", today_dt),
            ])
            for leave in to_send_parental_leaves:
                mail_template.send_mail(leave.id)
        return super(ShiftLeave, self).send_mail_reminder_non_defined_leaves()
