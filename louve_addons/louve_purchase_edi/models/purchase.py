# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import models, api, fields


class EdiMappingLines(models.Model):
    _name = 'edi.mapping.lines'

    config_id = fields.Many2one(comodel_name="edi.config.system")
    position = fields.Integer(string="Position", required=True)
    delimiter = fields.Char(string="Delimiter", required=True)
    required_field = fields.Boolean(string="Required")
    size = fields.Integer(string="Size", required=True)
    decimal_precision = fields.Integer(string="Decimal precision")
