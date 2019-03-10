# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.io/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import models, api, fields


class EdiMappingLines(models.Model):
    _name = 'edi.mapping.lines'
    _order = 'position'

    config_id = fields.Many2one(comodel_name="edi.config.system")
    sequence = fields.Integer(string="Sequence", required=True, default=1)
    position = fields.Integer(string="Position", required=True)
    value = fields.Char(string="Python code", help="Use python code to generate your order file, using methods defined"
                                                   "on the configuration system model", required=True)


class EdiPriceMapping(models.Model):
    _name = 'edi.price.mapping'
    _order = 'position'

    sequence = fields.Integer(string="Sequence", default=1)
    position = fields.Integer(string="Position", required=True)
    price_config_id = fields.Many2one(comodel_name="edi.config.system")
    mapping_field_id = fields.Many2one(comodel_name="ir.model.fields",
                                       domain="[('model', '=', 'supplier.price.list')]", string="Prices mapping field")
    name = fields.Char(string="Zone description")
    sequence_start = fields.Integer(string="Sequence start")
    sequence_end = fields.Integer(string="Sequence end")
    is_numeric = fields.Boolean(string="Is numeric ?")
    is_date = fields.Boolean(string="Is a date?")
    decimal_precision = fields.Integer(string="Decimal precision")


class EdiBleMapping(models.Model):
    _name = 'edi.ble.mapping'
    _order = 'position'

    sequence = fields.Integer(string="Sequence", default=1)
    position = fields.Integer(string="Position", required=True)
    ble_config_id = fields.Many2one(comodel_name="edi.config.system")
    mapping_field_id = fields.Many2one(comodel_name="ir.model.fields", string="Prices mapping field")
    name = fields.Char(string="Zone description")
    sequence_start = fields.Integer(string="Sequence start")
    sequence_end = fields.Integer(string="Sequence end")
