# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _


class ShiftCounterEvent(models.Model):
    _inherit = 'shift.counter.event'

    holiday_id = fields.Many2one('shift.holiday', string="Holiday")
