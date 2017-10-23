# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields

LEAVE_TYPE_STATE_SELECTION = [
    ('exempted', 'Exempted'),
    ('vacation', 'On Vacation'),
]


class ShiftLeaveType(models.Model):
    _name = 'shift.leave.type'

    name = fields.Char(string='Name', required=True)

    active = fields.Boolean(string='Active', default=True)

    state = fields.Selection(
        selection=LEAVE_TYPE_STATE_SELECTION, default='vacation', help=" State"
        " of the people during the leave.\n * 'Exempted' : The customer"
        " can buy.\n * 'On vacation' : The customer can not buy.")

    require_stop_date = fields.Boolean(
        string='Required Stop Date', default=True, help="Uncheck this box"
        " if the Leaves associated to this Leave Types can be without Stop"
        " Date. \nTypical Sample : Permanent Disability.")
