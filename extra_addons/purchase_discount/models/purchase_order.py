# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Pedro M. Baeza
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('discount', 'order_id.partner_id')
    def _compute_amount(self):
        prices = {}
        for line in self:
            if line.discount:
                prices[line.id] = line.price_unit
                line.price_unit *= (1 - line.discount / 100.0)

                # Rounding the Price Unit based on the Partner's Discount
                # computation
                partner_disc_computation = \
                    line.order_id.partner_id.discount_computation
                currency = line.order_id.currency_id
                if partner_disc_computation == 'unit_price':
                    line.price_unit = currency.round(line.price_unit)

            super(PurchaseOrderLine, line)._compute_amount()
            # restore prices
            if line.discount:
                line.price_unit = prices[line.id]

    discount = fields.Float(
        string='Discount (%)', digits_compute=dp.get_precision('Discount'))

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]
