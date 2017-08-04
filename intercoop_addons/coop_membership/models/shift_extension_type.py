# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models


class ShiftExtensionType(models.Model):
    _inherit = 'shift.extension.type'

    extension_method = fields.Selection(
        selection=[('fixed_duration', 'Fixed Duration'),
                   ('to_next_regular_shift', 'Extend to next regular shift')],
        required=True, string="Extension Method",
        default="fixed_duration")

    # Required will be added in from view
    duration = fields.Integer(required=False)
