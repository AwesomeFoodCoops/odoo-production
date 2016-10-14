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
from datetime import datetime, timedelta


class ShiftTicket(models.Model):
    _inherit = 'event.event.ticket'
    _name = 'shift.ticket'
    _description = 'Shift Ticket'

    SHIFT_TYPE_SELECTION = [
        ('standard', 'Standard'),
        ('ftop', 'FTOP'),
    ]

    shift_type = fields.Selection(
        selection=SHIFT_TYPE_SELECTION, string='Shift type',
        compute='compute_shift_type', store=True)

    name = fields.Char(translate=False)
    shift_id = fields.Many2one(
        'shift.shift', "Shift", required=True, ondelete='cascade')
    event_id = fields.Many2one(required=False)
    product_id = fields.Many2one(
        default=lambda self: self._default_product_id(),
        domain=[("shift_type_id", "!=", False)],)
    registration_ids = fields.One2many(
        'shift.registration', 'shift_ticket_id', 'Registrations')
    date_begin = fields.Datetime(related="shift_id.date_begin")
    begin_date_string = fields.Char(
        string='Begin Date', compute='_compute_begin_date_fields', store=True,)
    user_id = fields.Many2one(
        'res.partner', related="shift_id.user_id", store=True)

    @api.multi
    @api.depends('date_begin')
    def _compute_begin_date_fields(self):
        for ticket in self:
            ticket.begin_date_string = ticket.date_begin and datetime.strftime(
                datetime.strptime(ticket.date_begin, "%Y-%m-%d %H:%M:%S") +
                timedelta(hours=2), "%d/%m/%Y %H:%M:%S") or False

    @api.model
    def _default_product_id(self):
        try:
            product = self.env['ir.model.data'].get_object(
                'coop_shift', 'product_product_event')
            return product.id
        except ValueError:
            return False

    seats_availability = fields.Selection(compute='_compute_seats')
    seats_reserved = fields.Integer(compute='_compute_seats')
    seats_available = fields.Integer(compute='_compute_seats')
    seats_unconfirmed = fields.Integer(compute='_compute_seats')
    seats_used = fields.Integer(compute='_compute_seats',)

    @api.depends('product_id')
    @api.multi
    def compute_shift_type(self):
        for ticket in self:
            if ticket.product_id.id ==\
                    self.env.ref("coop_shift.product_product_shift_ftop").id:
                ticket.shift_type = 'ftop'
            else:
                ticket.shift_type = 'standard'

    @api.multi
    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        """ Determine reserved, available, reserved but unconfirmed and used
            seats. """
        # initialize fields to 0 + compute seats availability
        for ticket in self:
            ticket.seats_availability = 'unlimited' if ticket.seats_max == 0\
                else 'limited'
            ticket.seats_unconfirmed = ticket.seats_reserved =\
                ticket.seats_used = ticket.seats_available = 0
        # aggregate registrations by ticket and by state
        if self.ids:
            state_field = {
                'draft': 'seats_unconfirmed',
                'open': 'seats_reserved',
                'done': 'seats_used',
            }
            query = """ SELECT shift_ticket_id, state, count(shift_id)
                        FROM shift_registration
                        WHERE shift_ticket_id IN %s
                        AND state IN ('draft', 'open', 'done')
                        GROUP BY shift_ticket_id, state
                    """
            self._cr.execute(query, (tuple(self.ids),))
            for shift_ticket_id, state, num in self._cr.fetchall():
                ticket = self.browse(shift_ticket_id)
                ticket[state_field[state]] += num
        # compute seats_available
        for ticket in self:
            if ticket.seats_max > 0:
                ticket.seats_available = ticket.seats_max - (
                    ticket.seats_reserved + ticket.seats_used)

    @api.multi
    @api.constrains('registration_ids', 'seats_max')
    def _check_seats_limit(self):
        for ticket in self:
            if ticket.seats_max and ticket.seats_available < 0:
                raise UserError(_('No more available seats for the ticket'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        price = self.product_id.list_price if self.product_id else 0
        return {'value': {'price': price}}
