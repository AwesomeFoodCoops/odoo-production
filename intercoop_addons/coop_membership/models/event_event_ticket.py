# -*- coding: utf-8 -*-

from openerp import api, models, fields


class event_ticket(models.Model):
    _inherit = 'event.event.ticket'

    is_discovery_meeting_event = fields.Boolean(
        string='Discovery Meeting Event', store=True)
