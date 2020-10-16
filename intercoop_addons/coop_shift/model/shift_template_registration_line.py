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

from openerp import _, api, fields, models

from openerp.exceptions import ValidationError
from datetime import datetime
import pytz


STATES = [
    ('cancel', 'Cancelled'),
    ('draft', 'Unconfirmed'),
    ('open', 'Confirmed'),
    ('done', 'Attended'),
    ('absent', 'Absent'),
    ('waiting', 'Waiting'),
    ('excused', 'Excused'),
    ('replaced', 'Replaced'),
    ('replacing', 'Replacing'),
]


class ShiftTemplateRegistrationLine(models.Model):
    _name = 'shift.template.registration.line'
    _description = 'Attendee Line'
    _order = 'date_begin desc'

    registration_id = fields.Many2one(
        'shift.template.registration', string='Registration', required=True,
        ondelete='cascade')
    date_begin = fields.Date("Begin Date", required=True)
    date_end = fields.Date("End Date")
    state = fields.Selection(STATES, string="State", default="open")
    shift_registration_ids = fields.One2many(
        'shift.registration', 'tmpl_reg_line_id',
        'Registrations',)
    partner_id = fields.Many2one(
        related="registration_id.partner_id", store=True)
    shift_template_id = fields.Many2one(
        related="registration_id.shift_template_id")
    shift_ticket_id = fields.Many2one(
        related="registration_id.shift_ticket_id")
    is_current = fields.Boolean(
        string="Current", compute="_compute_current", multi="current")
    is_past = fields.Boolean(
        string="Past", compute="_compute_current", multi="current")
    is_future = fields.Boolean(
        string="Future", compute="_compute_current", multi="current")

    leave_id = fields.Many2one('shift.leave', string='Leave')

    # constraints Section
    @api.multi
    @api.constrains('date_begin', 'date_end')
    def _check_dates(self):
        for leave in self:
            if leave.date_end and leave.date_end < leave.date_begin:
                raise ValidationError(_(
                    "Stop Date should be greater than Start Date."))
            leave._check_over_lap()

    @api.multi
    def _check_over_lap(self):
        self.ensure_one()
        lines = self.partner_id.tmpl_reg_line_ids
        for line in lines:
            if (
                (line.date_begin <= self.date_end or not self.date_end)
                and (line.date_end >= self.date_begin or not line.date_end)
                and line.id != self.id
            ):
                raise ValidationError(_(
                    "You can't register this line because it would "
                    "create an overlap with another line for this member.\n\n"
                    "Line: %s - %s\n"
                    "Overlap: %s - %s") % (
                        self.date_begin, self.date_end,
                        line.date_begin, line.date_end))

    @api.multi
    def _compute_current(self):
        for line in self:
            now = fields.Datetime.now()
            line.is_current = False
            line.is_past = False
            line.is_future = False
            if (line.date_begin and line.date_begin > now):
                line.is_future = True
            elif (line.date_end and line.date_end < now):
                line.is_past = True
            else:
                line.is_current = True

    @api.model
    def create(self, vals):
        begin = vals.get('date_begin', False)
        end = vals.get('date_end', False)

        st_reg_id = vals.get('registration_id', False)
        if not st_reg_id:
            shift_template_id = vals.get('shift_template_id', False)
            partner_id = vals.get('partner_id', False)
            reg_ids = self.env['shift.template'].browse(shift_template_id).\
                registration_ids.filtered(
                    lambda r: r.partner_id.id == partner_id)
            st_reg_id = reg_ids and reg_ids[0].id or False
            vals['registration_id'] = st_reg_id
        if not st_reg_id:
            st_reg_id = self.env['shift.template.registration'].with_context({
                'no_default_line': True}).create(
                {
                    'shift_template_id': shift_template_id,
                    'partner_id': partner_id,
                    'shift_ticket_id': vals.get('shift_ticket_id', False),

                }).id
            vals['registration_id'] = st_reg_id

        st_reg = self.env['shift.template.registration'].browse(st_reg_id)
        partner = st_reg.partner_id

        shifts = st_reg.shift_template_id.shift_ids.filtered(
            lambda s, b=begin, e=end: (s.date_begin > b or not b) and
            (s.date_end < e or not e) and (s.state != 'done'))

        v = {
            'partner_id': partner.id,
            'state': vals.get('state', 'open')
        }

        created_registrations = []
        for shift in shifts:
            ticket_id = shift.shift_ticket_ids.filtered(
                lambda t: t.product_id == st_reg.shift_ticket_id.product_id)
            if ticket_id:
                ticket_id = ticket_id[0]
            else:
                shift.write({
                    'shift_ticket_ids': [(0, 0, {
                        'name': st_reg.shift_ticket_id.name,
                        'product_id': st_reg.shift_ticket_id.product_id.id,
                        'seats_max': st_reg.shift_ticket_id.seats_max,
                    })]
                })
                ticket_id = shift.shift_ticket_ids.filtered(
                    lambda t: t.product_id ==
                    st_reg.shift_ticket_id.product_id)[0]
            values = dict(v, **{
                'shift_id': shift.id,
                'shift_ticket_id': ticket_id.id,
                'template_created': True,
            })
            created_registrations.append((0, 0, values))

        vals['shift_registration_ids'] = created_registrations
        return super(ShiftTemplateRegistrationLine, self.with_context(
            dict(self.env.context, **{'creation_in_progress': True}))).create(
            vals)

    @api.multi
    def write(self, vals):
        res = super(ShiftTemplateRegistrationLine, self).write(vals)
        self.mapped(lambda s: s.partner_id)._compute_registration_counts()
        for line in self:
            bypass_leave_change_check = self._context.get(
                'bypass_leave_change_check', False)
            if not bypass_leave_change_check and line.leave_id:
                raise ValidationError(_(
                    "You cannot make changes on this template registration. "
                    "Please make your changes directly on the leave recorded "
                    "for this period. You will need to cancel it then set to "
                    "draft before you can make required changes.\n\n"
                    "Registration: (ID: %s) - %s") % (
                        line, line.partner_id.name))

            sr_obj = self.env['shift.registration']
            st_reg = line.registration_id
            partner = st_reg.partner_id

            state = vals.get('state', line.state)
            begin = vals.get('date_begin', line.date_begin)
            end = vals.get('date_end', line.date_end)

            # for linked registrations
            for sr in line.shift_registration_ids:
                shift = sr.shift_id

                # Convert the datetime in shift to local date
                shift_date_begin = self.convert_local_date(shift.date_begin)
                shift_date_end = self.convert_local_date(shift.date_end)

                # if shift is done, pass
                if shift.state == "done":
                    continue
                # if dates ok, just update state
                if sr.state in ['draft', 'open', 'waiting']:
                    if (shift_date_begin >= begin or not begin) and\
                            (shift_date_end <= end or not end):
                        sr.state = state
                    # if dates not ok, unlink the shift_registration
                    else:
                        sr.unlink()

            # for shifts within dates: if partner has no registration, create
            # it
            shifts = st_reg.shift_template_id.shift_ids.filtered(
                lambda s, b=begin, e=end: (
                    self.convert_local_date(s.date_begin) >= b or not b) and (
                    self.convert_local_date(s.date_end) <= e or not e) and (
                    s.state not in ('done', 'cancel')))

            for shift in shifts:
                found = partner_found = False
                for registration in shift.registration_ids:
                    if registration.partner_id == partner:
                        partner_found = registration
                    if registration.tmpl_reg_line_id == line:
                        found = True
                        break

                if not found:
                    if partner_found:
                        partner_found.tmpl_reg_line_id = line
                        partner_found.state = state
                    else:
                        ticket_id = shift.shift_ticket_ids.filtered(
                            lambda t: t.product_id ==
                            st_reg.shift_ticket_id.product_id)
                        if ticket_id:
                            ticket_id = ticket_id[0]
                            values = {
                                'partner_id': partner.id,
                                'state': state,
                                'shift_id': shift.id,
                                'shift_ticket_id': ticket_id.id,
                                'tmpl_reg_line_id': line.id,
                                'template_created': True,
                            }
                            sr_obj.create(values)
        return res

    @api.multi
    def unlink(self):
        for strl in self:
            for reg in strl.shift_registration_ids:
                reg.unlink()
        return super(ShiftTemplateRegistrationLine, self).unlink()

    @api.model
    def convert_local_date(self, timeutc):
        '''
        @Function to convert UTC time to Local Time and return the local date
        '''
        if not timeutc:
            return False
        tz_name = self._context.get('tz') or self.env.user.tz
        dateutc_obj = datetime.strptime(timeutc, '%Y-%m-%d %H:%M:%S')
        utc_timestamp = pytz.utc.localize(
            dateutc_obj, is_dst=False)
        context_tz = pytz.timezone(tz_name)
        datelocal_obj = utc_timestamp.astimezone(context_tz)

        return datelocal_obj.strftime('%Y-%m-%d')
