# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.osv import expression


class PurchaseBillUnion(models.Model):
    _inherit = 'purchase.bill.union'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            args = args or []
            domain = ['|',
                ('name', operator, name),
                ('reference', operator, name),
            ]
            args = expression.AND([args, domain])
            name = ''
        return super(PurchaseBillUnion, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
