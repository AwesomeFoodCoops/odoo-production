# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    amount_untaxed = fields.Float(compute='_compute_amount_untaxed',
                                  string='Amount Untaxed',
                                  digits=0, store=True)

    @api.depends('statement_ids',
                 'lines.price_subtotal',
                 'lines.discount')
    def _compute_amount_untaxed(self):
        for order in self:
            currency = order.pricelist_id.currency_id
            order.amount_untaxed = currency.round(
                sum(line.price_subtotal for line in order.lines))
