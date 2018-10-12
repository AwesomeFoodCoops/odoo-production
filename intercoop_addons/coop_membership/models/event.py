# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import Warning


class event_event(models.Model):
    _inherit = 'event.event'

    is_discovery_meeting = fields.Boolean('Discovery Meeting')
    room_preparation_member_ids = fields.Many2many(
        'res.partner',
        'rel_preparation_member_ids',
        string="Room preparation delegates",
        domain="[('is_member', '=', True)]",
        help="1 or 2 people to prepare the room (chairs, tables, ...)"
    )
    leader_member_ids = fields.Many2many(
        'res.partner',
        'rel_leader_member_ids',
        string="Meeting leaders",
        domain="[('is_member', '=', True)]",
        help="1 or 2 people"
    )
    subscription_help_member_ids = fields.Many2many(
        'res.partner',
        'rel_help_member_ids',
        string="Subscription helpers",
        domain="[('is_member', '=', True)]",
        help="2 people (+ 1 or 2 members in shift)"
    )
    subscription_member_ids = fields.Many2many(
        'res.partner',
        'rel_subscription_member_ids',
        string="Subscription delegates",
        domain="[('is_member', '=', True)]",
        help="2 or 3 people"
    )
    seats_availability = fields.Selection(default='limited')
    seats_max = fields.Integer(
        default=lambda self: self._get_default_seats_max())

    @api.model
    def _get_default_seats_max(self):
        event_confg = self.env['event.config.settings'].sudo().search(
            [], limit=1, order="id desc")
        return event_confg and event_confg.seats_max or 0

    @api.one
    def button_done(self):
        registration_pending = self.registration_ids.filtered(
            lambda r: r.state not in ['cancel', 'done'])
        if registration_pending:
            raise Warning(_("You cannot close this event. Please review attendances and mark all attendees as absent or present."))
        res = super(event_event, self).button_done()
        registration_absent = self.registration_ids.filtered(
            lambda r: r.state == 'cancel')
        partner_absent = registration_absent.mapped('partner_id')
        partner_absent.unlink()
        registration_absent.unlink()
        return res