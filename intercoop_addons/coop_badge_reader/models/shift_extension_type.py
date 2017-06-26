# -*- coding: utf-8 -*-

from openerp import fields, models


class ShiftExtensionType(models.Model):
    _inherit = "shift.extension.type"

    is_grace_period = fields.Boolean("Is Grace Period")
