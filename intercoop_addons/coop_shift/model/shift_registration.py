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

from openerp import models, fields, api, _
from openerp.exceptions import UserError
from datetime import timedelta, datetime
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


class ShiftRegistration(models.Model):
    _inherit = 'event.registration'
    _name = 'shift.registration'
    _description = 'Attendee'
    _order = 'shift_ticket_id,name'

    SHIFT_TYPE_SELECTION = [
        ('standard', 'Standard'),
        ('ftop', 'FTOP'),
    ]

    shift_type = fields.Selection(
        selection=SHIFT_TYPE_SELECTION, string='Shift type',
        related='shift_ticket_id.shift_type', store=True)

    event_id = fields.Many2one(required=False)
    shift_id = fields.Many2one(
        'shift.shift', string='Shift', required=True, ondelete='cascade')
    email = fields.Char(readonly=True, related='partner_id.email')
    phone = fields.Char(readonly=True, related='partner_id.phone')
    name = fields.Char(readonly=True, related='partner_id.name', store=True)
    partner_id = fields.Many2one(required=True)
    user_ids = fields.Many2many(related="shift_id.user_ids")
    shift_ticket_id = fields.Many2one(
        'shift.ticket', 'Shift Ticket', required=True, ondelete="cascade")
    shift_ticket_product_id = fields.Many2one(
        'product.product', 'Ticket Product',
        related='shift_ticket_id.product_id', store=True)
    state = fields.Selection(STATES)
    tmpl_reg_line_id = fields.Many2one(
        'shift.template.registration.line', "Template Registration Line")
    date_begin = fields.Datetime(related="shift_id.date_begin", store=True)
    date_end = fields.Datetime(related="shift_id.date_end")
    replacing_reg_id = fields.Many2one(
        'shift.registration', "Replacing Registration", required=False)
    replaced_reg_id = fields.Many2one(
        'shift.registration', "Replaced Registration", required=False)
    template_created = fields.Boolean("Created by a Template", default=False)
    is_related_shift_ftop = fields.Boolean(
        compute='compute_is_related_shift_ftop', store=False)

    replacing_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Replacing Member",
        related="replacing_reg_id.partner_id",
        store=True
    )

    exchange_state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('replacing', 'Replacing'),
        ('replaced', 'Replaced')
    ], string="Exchange Status", default='draft')

    is_technical = fields.Boolean(
        compute='_compute_is_technical',
        store=True
    )

    _sql_constraints = [(
        'shift_registration_uniq',
        'unique (shift_id, partner_id)',
        'This partner is already registered on this Shift !'),
    ]

    @api.multi
    @api.depends('shift_id.shift_template_id.is_technical')
    def _compute_is_technical(self):
        for registration in self:
            registration.is_technical = \
                registration.shift_id.shift_template_id.is_technical

    @api.multi
    def compute_is_related_shift_ftop(self):
        '''
        @Function to compute the value for field `is_related_shift_ftop`
            Set value to True if related Shift is in type of FTOP, and False
            otherwise
        '''
        for registration in self:
            if registration.shift_id and \
                    registration.shift_id.shift_type_id and \
                    registration.shift_id.shift_type_id.is_ftop:
                registration.is_related_shift_ftop = True
            else:
                registration.is_related_shift_ftop = False

    @api.multi
    def button_reg_absent(self):
        for reg in self:
            if reg.event_id.date_begin <= fields.Datetime.now():
                reg.state = 'absent'
            else:
                raise UserError(_("You must wait for the starting day of the\
                    shift to do this action."))

    @api.multi
    def button_reg_excused(self):
        for reg in self:
            if reg.event_id.date_begin <= fields.Datetime.now():
                reg.state = 'excused'
            else:
                raise UserError(_("You must wait for the starting day of the\
                    shift to do this action."))

    @api.multi
    @api.onchange("shift_id")
    def onchange_shift_id(self):
        FTOP_product = self.env.ref("coop_shift.product_product_shift_ftop")
        for reg in self:
            reg.shift_ticket_id = reg.shift_id.shift_ticket_ids.filtered(
                lambda t: t.product_id == FTOP_product)

    @api.model
    def create(self, vals):
        if not vals.get('template_created', False):
            shift_ticket_id = vals.get('shift_ticket_id', False)
            shift_ticket = self.env['shift.ticket'].browse(shift_ticket_id)
            if (
                shift_ticket
                and shift_ticket.shift_type != 'standard'
                and shift_ticket.seats_max
                and shift_ticket.seats_available <= 0
            ):
                raise UserError(_('No more available seats for this ticket'))
        reg_id = super(ShiftRegistration, self).create(vals)
        if reg_id.shift_id.state == "confirm":
            reg_id.confirm_registration()
            # Restore the state
            if (
                reg_id.tmpl_reg_line_id
                and reg_id.state != reg_id.tmpl_reg_line_id.state
            ):
                reg_id.state = reg_id.tmpl_reg_line_id.state
        return reg_id

    @api.multi
    def confirm_registration(self):
        super(ShiftRegistration, self).confirm_registration()
        for reg in self:
            onsubscribe_schedulers = reg.shift_id.shift_mail_ids.filtered(
                lambda s: s.interval_type == 'after_sub')
            onsubscribe_schedulers.execute()

    @api.one
    @api.constrains('event_ticket_id', 'state')
    def _check_ticket_seats_limit(self):
        return True
