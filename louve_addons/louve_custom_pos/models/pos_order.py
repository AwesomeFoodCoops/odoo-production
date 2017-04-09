# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste (julien.weste@akretion.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    amount_total = fields.Float(store=True)

    def _init_amount_total(self, cr, uid, ids=None, context=None):
        order_ids = self.search(cr, uid, [], context=context)
        orders = self.browse(cr, uid, order_ids, context=context)
        for order in orders:
            currency = order.pricelist_id.currency_id
            amount_untaxed = currency.round(
                sum(line.price_subtotal for line in order.lines))
            order.amount_total = currency.round(
                order.amount_tax + amount_untaxed)
