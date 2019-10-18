# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    transform_expr = fields.Char(
        'Transform Expression',
        help=(
            'Python Expression used to transform the value '
            'read in the barcode.\n'
            'ie: value / 0.15\n\n'
            'Available variables:\n'
            '- value: the original value read in the barcode.\n'
            '- code: the simplified barcode code\n'
            '- barcode: the complete barcode.\n'
        ),
    )
