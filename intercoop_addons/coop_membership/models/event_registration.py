# -*- coding: utf-8 -*-

from openerp import models, fields


class event_registration(models.Model):
    _inherit = 'event.registration'

    is_discovery_meeting_event = fields.Boolean(
        'Discovery Meeting Event',
        related='event_id.is_discovery_meeting')
