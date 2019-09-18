# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ShiftExtensionType(models.Model):
    _name = 'shift.extension.type'
    _description = 'Shift Extension Type'

    name = fields.Char(string='Name', required=True)

    duration = fields.Integer(
        string='Duration', required=True, help="Default duration (in days)")
