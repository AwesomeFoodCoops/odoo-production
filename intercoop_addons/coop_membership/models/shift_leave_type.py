# -*- coding: utf-8 -*-

from openerp import fields, models


class ShiftLeaveType(models.Model):
    _inherit = 'shift.leave.type'

    is_temp_leave = fields.Boolean(string='Temporary Leave', default=False)
    is_incapacity = fields.Boolean(string='Incapacity', default=False)
