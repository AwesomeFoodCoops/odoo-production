# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

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
        'shift.template.registration',
        string='Registration',
        required=True,
        ondelete='cascade',
    )
    date_begin = fields.Date("Begin Date", required=True)
    date_end = fields.Date("End Date")
    state = fields.Selection(STATES, string="State", default="open")
    shift_registration_ids = fields.One2many(
        'shift.registration', 'tmpl_reg_line_id',
        'Registrations',)
    partner_id = fields.Many2one(
        related="registration_id.partner_id", store=True, readonly=False)
    shift_template_id = fields.Many2one(
        related="registration_id.shift_template_id", readonly=False)
    shift_ticket_id = fields.Many2one(
        related="registration_id.shift_ticket_id", readonly=False)
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
                line.id != self.id
                and (not self.date_end or line.date_begin <= self.date_end)
                and (not line.date_end or line.date_end >= self.date_begin)
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
            now = fields.Date.context_today(self)
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
        if begin:
            begin = fields.Date.from_string(begin)

        if end:
            end = fields.Date.from_string(end)

        st_reg_id = vals.get('registration_id', False)
        if not st_reg_id:
            registration_id = self.env['shift.template.registration'].search(
                [
                    ('partner_id', '=', vals.get('partner_id')),
                    ('shift_template_id', '=', vals.get('shift_template_id')),
                ], limit=1)
            st_reg_id = registration_id and registration_id.id or False
            vals['registration_id'] = st_reg_id
        if not st_reg_id:
            registration_id = \
                self.env['shift.template.registration'].with_context({
                    'no_default_line': True,
                }).create({
                    'shift_template_id': vals.get('shift_template_id'),
                    'partner_id': vals.get('partner_id'),
                    'shift_ticket_id': vals.get('shift_ticket_id', False),
                })
            st_reg_id = registration_id.id
            vals['registration_id'] = st_reg_id

        st_reg = self.env['shift.template.registration'].browse(st_reg_id)
        partner = st_reg.partner_id

        # Get shifts affected by this registratation line
        shift_domain = [
            ('shift_template_id', '=', st_reg.shift_template_id.id),
            ('state', '!=', 'done')
        ]
        if begin:
            shift_domain.append(('date_begin', '>', begin))
        if end:
            shift_domain.append(('date_end', '<', end))
        shifts = self.env['shift.shift'].search(shift_domain)

        # Compute registrations to create
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
                    lambda t: t.product_id == st_reg.shift_ticket_id.product_id
                )[0]
            values = dict(v, **{
                'shift_id': shift.id,
                'shift_ticket_id': ticket_id.id,
                'template_created': True,
            })
            created_registrations.append((0, 0, values))

        vals['shift_registration_ids'] = created_registrations
        return super(
            ShiftTemplateRegistrationLine,
            self.with_context(creation_in_progress=True)
        ).create(vals)

    @api.multi
    def write(self, vals):
        res = super(ShiftTemplateRegistrationLine, self).write(vals)
        self.mapped(lambda s: s.partner_id).sudo()._compute_registration_counts()
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
            if isinstance(end, str):
                end = fields.Date.from_string(end)
            if isinstance(begin, str):
                begin = fields.Date.from_string(begin)

            # Convert datetime to date
            if isinstance(begin, datetime.datetime):
                begin = begin.date()
            if isinstance(end, datetime.datetime):
                end = end.date()

            # Convert string to date (if coming from vals)
            if isinstance(begin, str):
                begin = fields.Date.from_string(begin)
            if isinstance(end, str):
                end = fields.Date.from_string(end)

            # for linked registrations
            for sr in line.shift_registration_ids:
                shift = sr.shift_id

                # if shift is done, pass
                if shift.state == "done":
                    continue
                # if dates ok, just update state
                if sr.state in ['draft', 'open', 'waiting']:
                    if (
                        (not begin or shift.date_begin.date() >= begin)
                        and (not end or shift.date_end.date() <= end)
                    ):
                        sr.state = state
                    # if dates not ok, unlink the shift_registration
                    else:
                        sr.unlink()

            # for shifts within dates: if partner has no registration, create
            # it
            shifts = st_reg.shift_template_id.shift_ids.filtered(
                lambda s, b=begin, e=end: (
                    not b or s.date_begin.date() >= b) and (
                    not e or s.date_end.date() <= e) and (
                    s.state != 'done'))

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
                            st_reg.shift_ticket_id.product_id)[0]
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
