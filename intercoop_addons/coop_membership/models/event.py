# -*- coding: utf-8 -*-

from openerp import api, models, fields


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
