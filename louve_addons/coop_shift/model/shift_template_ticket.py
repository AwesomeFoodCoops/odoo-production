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

from openerp import models, fields, api


class ShiftTemplateTicket(models.Model):
    _inherit = 'shift.ticket'
    _name = 'shift.template.ticket'
    _description = 'Shift Template Ticket'

    shift_id = fields.Many2one(required=False)

    shift_template_id = fields.Many2one(
        'shift.template', 'Template', required=True, ondelete='cascade')

    registration_ids = fields.One2many(
        'shift.template.registration', 'shift_ticket_id', 'Registrations')

    seats_availability = fields.Selection(compute='_compute_seats')

    seats_reserved = fields.Integer(compute='_compute_seats')

    seats_available = fields.Integer(compute='_compute_seats')

    seats_unconfirmed = fields.Integer(compute='_compute_seats')

    seats_used = fields.Integer(compute='_compute_seats')

    seats_future = fields.Integer(
        string="Future reservations", compute='_compute_seats')

    hide_in_member_space = fields.Boolean(
        string='Hide in Member Space', store=True,
        compute='_compute_hide_in_member_space')

    # Compute Section
    @api.multi
    @api.depends('shift_template_id.shift_type_id.is_ftop')
    def _compute_hide_in_member_space(self):
        for ticket in self:
            if ticket.shift_template_id.shift_type_id.is_ftop:
                ticket.hide_in_member_space = True
            else:
                ticket.hide_in_member_space = False

    @api.multi
    @api.depends('seats_max', 'registration_ids.line_ids')
    def _compute_seats(self):
        """ Determine reserved, available, reserved but unconfirmed and used
            seats. """
        # initialize fields to 0 + compute seats availability
        for ticket in self:
            ticket.seats_availability = 'unlimited' if ticket.seats_max == 0\
                else 'limited'
            ticket.seats_unconfirmed = ticket.seats_reserved =\
                ticket.seats_used = ticket.seats_available =\
                ticket.seats_future = 0
        # aggregate registrations by ticket and by state
        state_field = {
            'draft': 'seats_reserved',
            'open': 'seats_reserved',
            'done': 'seats_used',
        }

        # compute seats_available
        for ticket in self:
            for reg in ticket.registration_ids.filtered(
                    lambda r, states=state_field.keys(): r.state in states):
                if reg.is_current:
                    ticket[state_field[reg.state]] += 1
                if reg.is_future:
                    ticket['seats_future'] += 1
            if ticket.seats_max > 0:
                ticket.seats_available = ticket.seats_max - (
                    ticket.seats_reserved + ticket.seats_used)

    # Overload Section
    @api.multi
    def write(self, vals):
        new_vals = {}
        if "seats_max" in vals.keys():
            new_vals['seats_max'] = vals['seats_max']
        if "seats_availability" in vals.keys():
            new_vals['seats_availability'] = vals['seats_availability']
        for ticket in self:
            shifts = ticket.shift_template_id.shift_ids.filtered(
                lambda s: s.date_begin >= fields.Date.today())
            tickets = shifts.mapped(
                lambda s: s.shift_ticket_ids).filtered(
                lambda t, t2=ticket: t.shift_type == t2.shift_type)
            tickets.write(new_vals)
        return super(ShiftTemplateTicket, self).write(vals)
