# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

import pytz
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class ShiftRegistration(models.Model):
    _inherit = 'shift.registration'

    partner_id = fields.Many2one(
        domain=[('is_worker_member', '=', True)],
    )
    related_extension_id = fields.Many2one(
        'shift.extension',
        string="Related Shift Extensions",
    )
    related_shift_state = fields.Selection(
        string="Shift State",
        related="shift_id.state",
        store=False,
    )
    is_changed_team = fields.Boolean(
        string="Changed Team",
        default=False,
    )
    reduce_extension_id = fields.Many2one(
        'shift.extension',
        string="Reduced Extension",
    )

    @api.multi
    @api.constrains('shift_id')
    def _check_limit_of_registration(self):
        check_limit = self._context.get('check_limit', False)
        if not check_limit:
            return True
        self.check_limit_of_registration()
        return True

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].browse(vals.get('partner_id'))
        if (
            partner.is_unsubscribed
            and not self.env.context.get('creation_in_progress')
        ):
            raise UserError(_(
                "You can't register %s on a shift because "
                "he isn't registered on a template"
                ) % partner.name)
        res = super().create(vals)
        # Do not allow member with Up to date status register make up
        # in a ABCD shift on a ABCD tickets
        res.checking_shift_attendance()
        # Don't allow member register in leaving time
        res.check_leave_time()
        return res

    @api.multi
    def check_limit_of_registration(self):
        """
        Limit a number of registration for shift type FTOP per partner
        """
        company = self.env.user.company_id
        for rec in self.sudo():
            if rec.shift_id.date_begin:
                registrations = rec.partner_id.registration_ids.filtered(
                    lambda r, d=rec.shift_id.date_begin: (
                        r.date_begin
                        and r.date_begin.date() == d.date()
                        and r.state != 'cancel'
                        and r.shift_type == 'ftop'
                        and not r.is_related_shift_ftop
                    )
                )
                if (
                    company.max_registrations_per_day
                    and len(registrations) > company.max_registrations_per_day
                ):
                    raise ValidationError(_(
                        "The member %s already has %s registrations "
                        "in the same day. You can't program more.") % (
                            rec.partner_id.name,
                            len(registrations) - 1))
                # Check pass registration
                self.check_registration_period(
                    rec.shift_id.date_begin, rec.partner_id)
                limit = company.max_registration_per_period + 1
                next_regs = rec.partner_id.registration_ids.filtered(
                    lambda r, d=rec.shift_id.date_begin: (
                        r.date_begin
                        and r.date_begin.date() > d.date()
                        and r.state != 'cancel'
                        and r.shift_type == 'ftop'
                    )
                )[:limit]
                # Check next 10 days registration
                for next_reg in next_regs.sorted('date_begin'):
                    self.check_registration_period(
                        next_reg.date_begin, rec.partner_id)

    @api.model
    def check_registration_period(self, date_reg, partner):
        company = self.env.user.company_id
        check_begin_date = date_reg - timedelta(
            days=company.number_of_days_in_period - 1)
        registrations = partner.registration_ids.filtered(
            lambda r, d1=check_begin_date.date(), d2=date_reg.date(): (
                r.date_begin
                and r.date_begin.date() >= d1
                and r.date_begin.date() <= d2
                and r.state != 'cancel'
                and r.shift_type == 'ftop'
                and not r.is_related_shift_ftop
            )
        )
        if (
            company.max_registration_per_period
            and len(registrations) > company.max_registration_per_period
        ):
            raise ValidationError(_(
                "The member %s already has %s registrations in the "
                "preceding %s days. You can't program more.") % (
                    partner.name,
                    len(registrations) - 1,
                    company.number_of_days_in_period))

    @api.multi
    def action_create_extension(self):
        """
        @Function triggered by a button on Attendance tree view
        to create extension automatically for a member:
            - Extension Type: Extension
            - Start Date: registration start date
            - End Date: Next Shift Date
        """
        shift_extension_env = self.env['shift.extension']
        for registration in self:
            partner = registration.partner_id
            extension_type = self.env.ref(
                'coop_membership.shift_extension_type_extension')
            date_begin_date = fields.Date.context_today(self)
            ext_vals = {
                'partner_id':
                partner.id,
                'type_id':
                extension_type.id,
                'date_start':
                date_begin_date,
                'date_stop':
                shift_extension_env.suggest_extension_date_stop(
                    extension_type=extension_type,
                    partner=partner,
                    date_start=date_begin_date)
            }
            res_extension = shift_extension_env.create(ext_vals)
            registration.related_extension_id = res_extension.id

    @api.multi
    def button_reg_absent(self):
        # Store state before absent
        partner_cooperative_states = {}
        for reg in self:
            partner_cooperative_states[reg.partner_id] = reg.partner_id.cooperative_state
        res = super(ShiftRegistration, self).button_reg_absent()
        for reg in self:
            # Terminate the shift member
            if reg.template_created and reg.shift_type == 'standard':
                # Check for his next last shift registration
                last_shift_reg = self.search(
                    [('partner_id', '=', reg.partner_id.id),
                     ('template_created', '=', True),
                     ('date_begin', '<', reg.date_begin),
                     ('shift_type', '=', 'standard')],
                    order='date_begin desc',
                    limit=1)
                if last_shift_reg and last_shift_reg.state == 'absent':
                    # Check for any standard shift within
                    markup_shift_reg_count = self.search_count([
                        ('partner_id', '=', reg.partner_id.id),
                        ('date_begin', '>', last_shift_reg.date_begin),
                        ('date_begin', '<', reg.date_begin),
                        ('shift_type', '=', 'standard'),
                        ('state', 'in', ('done', 'replaced'))
                    ])
                    # If no markup reg found, set date end for the reg shift
                    if not markup_shift_reg_count:
                        # F#T61476 - [SQQ] Members going straight to unsubscribed after 2 consecutive absences
                        if partner_cooperative_states.get(
                                reg.partner_id, reg.partner_id.cooperative_state) == "up_to_date":
                            continue
                        tz_name = self._context.get('tz') or self.env.user.tz
                        utc_timestamp = pytz.utc.localize(reg.date_end,
                                                          is_dst=False)
                        context_tz = pytz.timezone(tz_name)
                        reg_date_end_tz = utc_timestamp.astimezone(context_tz)

                        final_date_end = reg_date_end_tz.strftime('%Y-%m-%d')
                        reg.tmpl_reg_line_id.date_end = final_date_end

                        # Sending the email to notify the member
                        partner = reg.partner_id

                        # Get the template xml from context
                        template_name = self.env.context.get(
                            "unsubscribe_email_template", False)
                        if not template_name:
                            template_name = "coop_membership.unsubscribe_email"
                        mail_template = \
                            self.env.ref(template_name)
                        if not mail_template:
                            continue
                        mail_template.send_mail(partner.id)
        return res

    @api.multi
    def write(self, vals):
        """
        Overide write function to update point counter for member
            + Standard:
                Add 1: Status is Attended / Replaced and template not created
                Deduct 2: Status is Absent
                Deduct 1: Status is Excused
            + FTOP
                Add 1: Status is Attended / Replaced
                Deduct 1: Status is Excused / Waiting and template created
                Deduct 1: Status is Absent
        """
        point_counter_env = self.env['shift.counter.event']
        vals_state = vals.get('state')
        for shift_reg in self:
            if vals_state != shift_reg.state:
                counter_vals = {}
                if shift_reg.shift_type == 'ftop':
                    if vals_state in ['done', 'replaced']:
                        reason = vals_state == 'done' and \
                            _('Attended') or \
                            _('Replaced')
                        counter_vals['point_qty'] = \
                            shift_reg.get_volants_supplemental_credit()
                        counter_vals['name'] = reason

                    elif vals_state in ['absent']:
                        counter_vals['point_qty'] = -1
                        counter_vals['name'] = _('Absent')

                        # Mark the point as ignored if the member is in
                        # ftop team and not belong to this team
                        if not shift_reg.tmpl_reg_line_id and \
                                shift_reg.partner_id.in_ftop_team:
                            counter_vals['ignored'] = True

                    elif vals_state in ['excused'] and \
                            shift_reg.template_created:
                        reason = vals_state == _('Excused')
                        counter_vals['point_qty'] = -1
                        counter_vals['name'] = reason

                elif shift_reg.shift_type == 'standard':
                    # Check if a member is belong to the template
                    if shift_reg.template_created:
                        if vals_state in ['absent']:
                            counter_vals['point_qty'] = -2
                            counter_vals['name'] = _('Absent')

                        elif vals_state in ['excused']:
                            counter_vals['point_qty'] = -1
                            counter_vals['name'] = _('Excused')
                    else:
                        if vals_state in ['done', 'replaced']:
                            reason = _('Attended')
                            counter_vals['point_qty'] = \
                                shift_reg.get_standard_supplemental_credit()
                            counter_vals['name'] = reason

                # Create Point Counter
                if counter_vals:
                    counter_vals.update({
                        'shift_id': shift_reg.shift_id.id,
                        'type': shift_reg.shift_type,
                        'partner_id': shift_reg.partner_id.id,
                    })

                    point_counter_env.sudo().with_context(
                        automatic=True).create(counter_vals)

                shift_reg.adjust_qty_on_holiday(vals_state)

                # Update point quantity of counter events when SET TO
                # UNCONFIRMED
                if vals_state == 'draft':
                    if shift_reg.partner_id:
                        counter_events = \
                            shift_reg.partner_id.counter_event_ids.filtered(
                                lambda c: c.shift_id.id ==
                                shift_reg.shift_id.id)
                        for event in counter_events:
                            last_qty = event.point_qty
                            event.write({
                                'point_qty':
                                0,
                                'notes':
                                'reset to 0 when clicking SET TO' +
                                ' UNCONFIRMED button for error correction' +
                                ' (original point quantity: %s)' % (last_qty)
                            })
                    shift_reg.related_extension_id.unlink()

        res = super(ShiftRegistration, self).write(vals)
        if 'template_created' in vals or 'shift_ticket_id' in vals:
            self.checking_shift_attendance()

        if 'template_created' in vals or 'shift_ticket_id' in\
                vals or 'shift_id' in vals:
            self.check_leave_time()
        return res

    @api.multi
    def get_standard_supplemental_credit(self):
        self.ensure_one()
        standard_point = 1
        is_standard_shift = self.shift_type == 'standard'
        is_standard_ticket = self.shift_ticket_id.shift_type == 'standard'
        not_belong_to_template = not self.template_created
        if is_standard_shift and is_standard_ticket and not_belong_to_template:
            current_template = self.shift_id.shift_template_id
            credit_config = self.env['shift.credit.config'].search([
                ('template_ids', 'in', current_template.ids),
                ('state', '=', 'active'),
                '&',
                ('apply_for_abcd', '=', True),
                '|',
                ('end_date', '=', False),
                ('end_date', '>', fields.Date.today()),
            ],
                limit=1)
            if credit_config:
                standard_point = float(credit_config.credited_make_ups)
        # Check current standard points
        balance_standard_point = 0
        partner = self.partner_id
        current_standard_point = sum([
            point_counter.point_qty
            for point_counter in partner.counter_event_ids
            if point_counter.type == 'standard'
        ])
        if standard_point + current_standard_point > balance_standard_point:
            standard_point = balance_standard_point - current_standard_point
        return standard_point

    @api.multi
    def get_volants_supplemental_credit(self):
        self.ensure_one()
        volant_point = 1
        is_ftop_shift = self.shift_type == 'ftop'
        is_ftop_ticket = self.shift_ticket_id.shift_type == 'ftop'
        in_ftop_team = self.partner_id.in_ftop_team
        if is_ftop_shift and is_ftop_ticket and in_ftop_team:
            current_template = self.shift_id.shift_template_id
            credit_config = self.env['shift.credit.config'].search([
                ('template_ids', 'in', current_template.ids),
                ('state', '=', 'active'),
                '&',
                ('apply_for_volants', '=', True),
                '|',
                ('end_date', '=', False),
                ('end_date', '>', fields.Date.today()),
            ],
                limit=1)
            if credit_config:
                volant_point = float(credit_config.credited_make_ups)
        return volant_point

    @api.multi
    def adjust_qty_on_holiday(self, vals):
        '''
            This method balance point qty for attendess that's on holiday
            flowwing the rule:
            Plus 2 in holiday type 0 make up and shift closed state
            with shift type standard and attendees was absent
            Plus 1 in holiday type 1 make up and shift open state
            for (shift type standard and attendees were exscued) or (shift
            type volant and attendees were absent or excused)
        '''
        self.ensure_one()
        point_counter_env = self.env['shift.counter.event']
        long_holiday = self.shift_id.long_holiday_id.filtered(
            lambda h: h.state == 'done')
        single_holiday = self.shift_id.single_holiday_id.filtered(
            lambda h: h.state == 'done')

        if vals in ['absent', 'excused']:
            counter_vals = {}
            if self.shift_type == 'standard' and self.template_created:
                if single_holiday:
                    if self.shift_id.state_in_holiday == 'closed':
                        if vals in ['absent']:
                            counter_vals.update({'point_qty': 2})
                        else:
                            counter_vals.update({'point_qty': 1})
                    elif self.shift_id.state_in_holiday == 'open' and \
                            vals in ['absent']:
                        counter_vals.update({'point_qty': 1})
                elif long_holiday:
                    if long_holiday.make_up_type == '0_make_up':
                        if vals in ['absent']:
                            counter_vals.update({'point_qty': 2})
                        else:
                            counter_vals.update({'point_qty': 1})
                    elif long_holiday.make_up_type == '1_make_up' and \
                            vals in ['absent']:
                        counter_vals.update({'point_qty': 1})
            elif self.shift_type == 'ftop':
                if single_holiday:
                    if self.shift_id.state_in_holiday == 'closed':
                        if (vals in ['absent']) or (vals in ['excused']
                                                    and self.template_created):
                            counter_vals.update({'point_qty': 1})
                elif long_holiday and not single_holiday:
                    if long_holiday.make_up_type == '0_make_up':
                        if (vals in ['absent']) or (vals in ['excused']
                                                    and self.template_created):
                            counter_vals.update({'point_qty': 1})
            if counter_vals:
                holiday_id = single_holiday and single_holiday.id \
                    or long_holiday.id
                counter_vals.update({
                    'shift_id': self.shift_id.id,
                    'type': self.shift_type,
                    'partner_id': self.partner_id.id,
                    'holiday_id': holiday_id,
                    'name': _('Balance qty for holiday')
                })

                point_counter_env.sudo().with_context(
                    automatic=True).create(counter_vals)
        return True

    @api.multi
    def balance_point_qty_ftop_shift(self, holiday_id, current_point, state):
        self.ensure_one()
        point_counter_env = self.env['shift.counter.event']
        point = 0
        if current_point >= 1:
            if state in ['0_make_up', 'closed']:
                point = 1
        else:
            if state in ['0_make_up', 'closed']:
                if self.reduce_extension_id and \
                        self.reduce_extension_id.reduce_deduction:
                    point = 1
                else:
                    point = 2
            else:
                point = 1
        # Create Point Counter
        if point > 0:
            point_counter_env.sudo().with_context({
                'automatic': True
            }).create({
                'name': _('Balance Qty For Shift Cloture'),
                'shift_id': self.shift_id.id,
                'type': 'ftop',
                'partner_id': self.partner_id.id,
                'point_qty': point,
                'holiday_id': holiday_id,
            })

    @api.multi
    def convert_format_datatime(self):
        for record in self:
            date = datetime.strftime(record.shift_id.date_begin_tz, '%d/%m/%Y')
            hour = datetime.strftime(record.shift_id.date_begin_tz, '%H')
            minute = datetime.strftime(record.shift_id.date_begin_tz, '%M')
            res = u'%s à %sh%s' % (date, hour, minute)
            return res

    @api.multi
    @api.onchange("shift_id")
    def onchange_shift_id(self):
        # Use the context value for default
        is_standard_ticket = self.env.context.get("is_standard_ticket", False)
        ticket_type_product = False
        if is_standard_ticket:
            ticket_type_product = \
                self.env.ref("coop_shift.product_product_shift_standard")
        else:
            ticket_type_product = \
                self.env.ref("coop_shift.product_product_shift_ftop")
        for reg in self:
            reg.shift_ticket_id = reg.shift_id.shift_ticket_ids.filtered(
                lambda t: t.product_id == ticket_type_product)

    @api.multi
    @api.depends('shift_id', 'date_begin')
    def name_get(self):
        result = []
        for registration in self:
            date_begin = ''
            if registration.date_begin:
                date_begin = fields.Date.to_string(registration.date_begin)
            name = registration.shift_id.name + (' ' + date_begin)
            result.append((registration.id, name))
        return result

    @api.multi
    def checking_shift_attendance(self):
        """
        @Function to check the attendance:
            - Do not allow member with Up to date status registers make up
            in a ABCD shift on a ABCD tickets
        """
        ignore_checking = \
            self.env.context.get('ignore_checking_attendance', False)
        if ignore_checking:
            return
        uptodate_list = []
        for shift_reg in self:
            shift_type = shift_reg.shift_id and \
                shift_reg.shift_id.shift_type_id
            if shift_type and not shift_type.is_ftop and \
                shift_reg.shift_type == 'standard' and \
                    not shift_reg.template_created and \
                    shift_reg.state not in ['replacing', 'replaced'] and \
                    shift_reg.exchange_state not in ['replacing', 'replaced'] \
                    and shift_reg.partner_id.working_state == 'up_to_date':
                uptodate_list.append('- [%s] %s' %
                                     (shift_reg.partner_id.barcode_base,
                                      shift_reg.partner_id.name))
        if uptodate_list:
            raise UserError(
                _("Warning! You cannot enter make-ups of " +
                  "the following members " + "as they are up-to-date: \n\n%s")
                % '\n'.join(uptodate_list))

    @api.multi
    def check_leave_time(self):
        """
        Check leaving time when register the shift
        Odoo should prevent them from scheduling shift that
        falls within the period of the leave
        """
        is_from_template = self._context.get('from_shift_template', False)
        for reg in self.sudo():
            # Get leave
            leaves = reg.partner_id.leave_ids.filtered(
                lambda l: (l.type_id.is_temp_leave or l.type_id.is_incapacity
                           ) and l.stop_date and l.state == 'done')

            for leave in leaves:
                if reg.date_end.date() >= leave.start_date and \
                        reg.date_begin.date() <= leave.stop_date:
                    if reg.shift_id.shift_type_id.is_ftop:

                        # Check attendee be crated from template
                        if is_from_template:
                            reg.state = 'waiting'
                        else:
                            # Get list attendee
                            partner_tmp_ids = reg.shift_id.shift_template_id. \
                                registration_ids.mapped('partner_id').ids
                            # Check attendde already be in template
                            if reg.partner_id.id in partner_tmp_ids:
                                reg.state = 'waiting'
                            else:
                                raise UserError(_("""
                                You can't register the shift (%s - %s)
                                that falls within the period of the
                                leave (%s - %s)""" % (reg.date_begin,
                                                      reg.date_end,
                                                      leave.start_date,
                                                      leave.stop_date
                                                      )))
                    elif not reg.shift_id.shift_type_id.is_ftop and \
                            leave.type_id.is_temp_leave:

                        # Check attendee be crated from template
                        if is_from_template:
                            reg.state = 'waiting'
                        else:
                            # Get list attendee
                            partner_tmp_ids = reg.shift_id.shift_template_id. \
                                registration_ids.mapped('partner_id').ids
                            # Check attendde already be in template
                            if reg.partner_id.id in partner_tmp_ids:
                                reg.state = 'waiting'
                            else:
                                raise UserError(_("""
                                You can't register the shift (%s - %s)
                                that falls within the period of the
                                leave (%s - %s)""" % (reg.date_begin,
                                                      reg.date_end,
                                                      leave.start_date,
                                                      leave.stop_date)))
