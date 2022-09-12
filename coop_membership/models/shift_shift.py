# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    standard_registration_ids = fields.One2many(
        "shift.registration", "shift_id",
        string="Standard Attendances",
        domain=[('shift_type', '=', 'standard')],
    )
    ftop_registration_ids = fields.One2many(
        "shift.registration", "shift_id",
        string="FTOP Attendances",
        domain=[('shift_type', '=', 'ftop')],
    )
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'), ('entry', 'Entry'),
        ('done', 'Done'),
        ],
    )

    shift_name_read = fields.Char(related='name', string="Shift Name Read")
    is_send_reminder = fields.Boolean("Send Reminder", default=False)

    long_holiday_id = fields.Many2one(
        'shift.holiday',
        string="Long Holiday",
    )
    single_holiday_id = fields.Many2one(
        'shift.holiday',
        string="Single Holiday",
    )
    holiday_id = fields.Many2one(
        'shift.holiday',
        string="Holiday",
        compute="_compute_holiday_id",
        help="Technical field",
    )
    state_in_holiday = fields.Selection(
        [('open', 'Open'), ('closed', 'Closed')],
        string="State in holiday",
    )
    holiday_single_state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
        ],
        related="single_holiday_id.state",
        string="Single Holiday Status",
    )
    required_skill_ids = fields.Many2many(
        related="shift_template_id.required_skill_ids",
        readonly=True,
    )

    @api.depends('long_holiday_id', 'single_holiday_id')
    def _compute_holiday_id(self):
        for rec in self:
            rec.holiday_id = rec.long_holiday_id or rec.single_holiday_id

    @api.multi
    def button_done(self):
        """
        @Overide the function to validate the registration before allowing
        marking the shift done
        """
        for shift in self:
            if not shift.shift_type_id.is_ftop:
                not_recorded_attendances = shift.registration_ids.filtered(
                    lambda x: x.state in ['draft', 'open'])
                if not_recorded_attendances:
                    shift_ticket_partners = []
                    for att in not_recorded_attendances:
                        ticket_name = att.shift_ticket_id.name or ''
                        partner_name = att.partner_id.name or ''
                        shift_ticket_partners.append(
                            "- [%s] %s" % (ticket_name, partner_name))
                    raise UserError(
                        _("Warning! You have not recorded the attendance " +
                          "for: \n\n%s") % '\n'.join(shift_ticket_partners))

        super(ShiftShift, self).button_done()

        # - Create Point for FTOP shift on cloturing
        #     + Deduct 1 if current point > 1
        #     + Deduct 2 if current point < 1
        point_counter_env = self.env['shift.counter.event']
        for shift in self:
            if shift.shift_type_id.is_ftop:
                long_holiday = shift.long_holiday_id
                single_holiday = shift.single_holiday_id
                for registration in shift.registration_ids:
                    partner = registration.partner_id
                    # Registration's state is waiting means the member is on
                    # vacation or exempted at the current shift. So, we don't
                    # deduct member's points
                    if registration.state == 'waiting':
                        continue

                    # Unignored all ignored counter
                    for counter in partner.counter_event_ids:
                        if counter.ignored:
                            counter.ignored = False

                    current_point = partner.final_ftop_point

                    if single_holiday and single_holiday.state == 'done':
                        holiday_id = single_holiday.id
                        registration.balance_point_qty_ftop_shift(
                            holiday_id, current_point, shift.state_in_holiday)
                    elif long_holiday and long_holiday.state == 'done':
                        holiday_id = long_holiday.id
                        registration.balance_point_qty_ftop_shift(
                            holiday_id, current_point,
                            long_holiday.make_up_type)
                    if current_point >= 1:
                        point = -1
                    else:
                        if registration.reduce_extension_id and \
                            registration.reduce_extension_id. \
                                reduce_deduction:
                            point = -1
                        else:
                            point = -2
                    # Create Point Counter
                    point_counter_env.sudo().with_context({
                        'automatic': True
                    }).create({
                        'name': _('Shift Cloture'),
                        'shift_id': shift.id,
                        'type': 'ftop',
                        'partner_id': partner.id,
                        'point_qty': point
                    })

    @api.multi
    def button_makeupok(self):
        """
        @Function trigger to change the state from Confirm to Entry
        """
        for shift in self:
            shift.state = 'entry'

            # Automatically mark attendance as "Attended" for
            # makeup (ABCD Member)
            """
            for reg in shift.registration_ids:
                if (
                    not reg.partner_id.in_ftop_team
                    and not reg.tmpl_reg_line_id
                    and reg.state != 'replacing'
                ):
                    reg.button_reg_close()
            """

    @api.multi
    def write(self, vals):
        res = super(ShiftShift, self).write(vals)
        # change to unconfirmed registrations to confirmed if this shift state
        # is `entry`
        for shift in self:
            if shift.state == 'entry':
                for reg in shift.standard_registration_ids:
                    if reg.state == 'draft':
                        reg.confirm_registration()
                for reg in shift.ftop_registration_ids:
                    if reg.state == 'draft':
                        reg.confirm_registration()
        return res

    @api.model
    def create(self, vals):
        self.update_create_vals(vals)
        res = super(ShiftShift, self).create(vals)
        return res

    @api.model
    def update_create_vals(self, vals):
        date_begin = vals.get("date_begin_tz")
        date_end = vals.get("date_end_tz")
        state = vals.get("state")
        if isinstance(date_begin, datetime):
            date_begin = date_begin.strftime(DF)
        if isinstance(date_end, datetime):
            date_end = date_end.strftime(DF)
        if state != "cancel" and date_begin and date_end:
            # find the holiday
            holidays = self.env["shift.holiday"].search([
                ("date_begin", "<=", date_begin),
                ("date_end", ">=", date_end),
                ("state", "not in", ("done", "cancel"))
            ])
            for holiday in holidays:
                if holiday.holiday_type == "long_period":
                    vals.update({
                        "long_holiday_id": holiday.id
                    })
                else:
                    vals.update({
                        "single_holiday_id": holiday.id
                    })

    @api.multi
    def open_in_holiday(self):
        for shift in self:
            if shift.state_in_holiday != 'open':
                shift.state_in_holiday = 'open'

    @api.multi
    def close_in_holiday(self):
        for shift in self:
            if shift.state_in_holiday != 'closed':
                shift.state_in_holiday = 'closed'

    @api.model
    def send_mail_reminder_ftop_members(self):
        shift_env = self.env['shift.shift']

        # get shifts 7 days later
        shifts = shift_env.search([
            ('is_send_reminder', '=', False),
            ('shift_type_id.is_ftop', '=', True),
            ('state', 'not in', ('cancel', 'done')),
            ('date_begin', '>=', fields.Date.context_today(self)),
            ('date_begin', '<=',
             (datetime.now() + timedelta(days=12)).strftime('%Y-%m-%d')),
            '|', ('long_holiday_id', '=', False),
            ('long_holiday_id.send_email_reminder', '=', True),
            '|', ('single_holiday_id', '=', False),
            ('single_holiday_id.send_email_reminder', '=', True),
        ])

        # Get attendent
        attendances = shifts.mapped("ftop_registration_ids")

        # Get attendences not former member
        partners = attendances.mapped("partner_id").filtered(
            lambda p: not p.is_former_member and p.active)

        # get all attendences's leaves
        leaves = partners.mapped('leave_ids')

        # get partner on leaves
        partner_on_leaves = self.env['res.partner']

        for shift in shifts:
            for leave in leaves:
                shift_begin = fields.Date.from_string(fields.Datetime.context_timestamp(
                    shift, shift.date_begin).strftime(DF))
                shift_end = fields.Date.from_string(fields.Datetime.context_timestamp(
                    shift, shift.date_end).strftime(DF))
                if leave.state == 'done' and (
                        not leave.stop_date or leave.stop_date >= shift_begin)  and \
                        leave.start_date <= shift_end:
                    partner_on_leaves |= leave.partner_id

        # remove partner on leaves
        partner_can_join = partners - partner_on_leaves

        attendences_to_send = attendances.filtered(
            lambda a: a.partner_id.id in partner_can_join.ids)

        # get mail template and send
        mail_template = self.env.ref(
            'coop_membership.coop_ftop_members_reminder_email')
        if mail_template:
            for attendence_to_send in attendences_to_send:
                mail_template.send_mail(attendence_to_send.id)

            # update sent reminder
            shifts.write({'is_send_reminder': True})

        return True
