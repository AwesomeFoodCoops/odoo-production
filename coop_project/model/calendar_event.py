# -*- coding: utf-8 -*-

from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    from_task = fields.Boolean()
    description = fields.Html(
        'Description', states={'done': [('readonly', True)]})
