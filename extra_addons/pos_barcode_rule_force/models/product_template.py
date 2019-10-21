# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    force_barcode_rule_id = fields.Many2one(
        'barcode.rule',
        string='Force Barcode Rule',
        help=(
            'If set, it will try to use this rule on the POS, '
            'regardless of the rule priority.'
        )
    )
