# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import models, fields, api


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
        compute='_compute_shift_type', store=True)

    shift_id = fields.Many2one(
        'shift.shift', "Shift", required=True, ondelete='cascade')

    event_id = fields.Many2one(required=False)

    product_id = fields.Many2one(
        default=lambda self: self._default_product_id(),
        domain=[("shift_type_id", "!=", False)],)

    registration_ids = fields.One2many(
        'shift.registration', 'shift_ticket_id', 'Registrations')

    date_begin = fields.Datetime(related="shift_id.date_begin", store=True)

    begin_date_string = fields.Char(
        string='Begin Date', compute='_compute_begin_date_fields', store=True,)

    user_ids = fields.Many2many(
        'res.partner', related="shift_id.user_ids")

    user_id = fields.Many2one(
        'res.partner', related="shift_id.user_id", store=True)

    hide_in_member_space = fields.Boolean(
        "Masquer dans l'Espace Membre", default=False,
        compute="_compute_hide_in_member_space", store=True)
    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'), ('done', 'Done')], related="shift_id.state",
        store=True)
    ticket_active = fields.Boolean(related="shift_id.active", store=True)

    @api.multi
    @api.depends('shift_id.shift_type_id.is_ftop')
    def _compute_hide_in_member_space(self):
        for ticket in self:
            if ticket.shift_id.shift_type_id.is_ftop:
                ticket.hide_in_member_space = True
            else:
                ticket.hide_in_member_space = False

    @api.multi
    @api.depends('date_begin')
    def _compute_begin_date_fields(self):
        for ticket in self:
            ticket.begin_date_string = \
                ticket.date_begin and\
                fields.Datetime.to_string(
                    ticket.date_begin + timedelta(hours=2)
                ) or False

    @api.model
    def _default_product_id(self):
        try:
            product = self.env['ir.model.data'].get_object(
                'coop_shift', 'product_product_event')
            return product.id
        except ValueError:
            return False

    seats_availability = fields.Selection(
        compute='_compute_seats', store=False, required=False)
    seats_reserved = fields.Integer(
        compute='_compute_seats', store=False)
    seats_available = fields.Integer(
        compute='_compute_seats', store=False)
    seats_unconfirmed = fields.Integer(
        compute='_compute_seats', store=False)
    seats_used = fields.Integer(
        compute='_compute_seats', store=False)

    @api.depends('product_id')
    @api.multi
    def _compute_shift_type(self):
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
            ticket.seats_unconfirmed = ticket.seats_reserved =\
                ticket.seats_used = ticket.seats_available = 0
        # aggregate registrations by ticket and by state
        if self.ids:
            state_field = {
                'draft': 'seats_reserved',
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
            ticket.seats_available = ticket.seats_max - (
                ticket.seats_reserved + ticket.seats_used)

    @api.onchange('product_id')
    def onchange_product_id(self):
        price = self.product_id.list_price if self.product_id else 0
        return {'value': {'price': price}}

    @api.constrains('registration_ids', 'seats_max')
    def _check_seats_limit(self):
        return True
