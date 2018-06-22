# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _


class ShiftTicket(models.Model):
    _inherit = 'shift.ticket'

    max_available_seat_standard = fields.Integer(
        string="Max Available Seats Standard",
        compute="_compute_seats_ticket",
        store=True)
    available_seat_standard = fields.Integer(
        string="Available Seats Standard",
        compute="_compute_seats_ticket",
        store=True)

    @api.multi
    @api.depends('shift_id', 'shift_id.shift_ticket_ids',
                 'shift_id.shift_ticket_ids.seats_max',
                 'shift_id.shift_ticket_ids.seats_available')
    def _compute_seats_ticket(self):
        for record in self:
            max_standard_seat = 0
            available_standard_seat = 0
            for ticket in record.shift_id.shift_ticket_ids:
                if ticket.shift_type == 'standard':
                    max_standard_seat += ticket.seats_max
                    available_standard_seat += ticket.seats_available
            record.available_seat_standard = available_standard_seat
            record.max_available_seat_standard = max_standard_seat

    @api.multi
    def update_shift_available_seat(self):
        for shift in self:
            shift._compute_seats_ticket()
        return True
