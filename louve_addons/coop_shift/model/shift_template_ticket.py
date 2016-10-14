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
        'shift.template', "Template", required=True, ondelete='cascade')
    registration_ids = fields.One2many(
        'shift.template.registration', 'shift_ticket_id', 'Registrations')

    seats_availability = fields.Selection(compute='_compute_seats')
    seats_reserved = fields.Integer(compute='_compute_seats')
    seats_available = fields.Integer(compute='_compute_seats')
    seats_unconfirmed = fields.Integer(compute='_compute_seats')
    seats_used = fields.Integer(compute='_compute_seats',)

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
            query = """ SELECT shift_ticket_id, state, count(shift_template_id)
                        FROM shift_template_registration
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
