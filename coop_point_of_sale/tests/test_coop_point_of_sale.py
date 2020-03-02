# -*- coding: utf-8 -*-
from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


class TestCoopPointOfSale(TestPointOfSaleCommon):

    def test_coop_pos_session(self):
        self.assertEqual(
            self.pos_order_session0.week_number,
            'C', "POS session week number should be in paid C.")
        self.assertEqual(
            self.pos_order_session0.week_day,
            'Tue', "POS session week day should be in paid Tue.")
        self.assertEqual(
            self.pos_order_session0.cycle,
            'CTue', "POS session cycle should be in paid CTue.")

    def test_coop_pos_order(self):
        order = self.PosOrder.create({
            'company_id': self.company_id,
            'partner_id': self.partner1.id,
            'pricelist_id': self.partner1.property_product_pricelist.id,
            'lines': [(0, 0, {
                'name': "OL/0001",
                'product_id': self.product3.id,
                'price_unit': 450,
                'discount': 5.0,
                'qty': 2.0,
                'tax_ids': [(6, 0, self.product3.taxes_id.ids)],
                'price_subtotal': 450 * (1 - 5/100.0) * 2,
                'price_subtotal_incl': 450 * (1 - 5/100.0) * 2,
            }), (0, 0, {
                'name': "OL/0002",
                'product_id': self.product4.id,
                'price_unit': 300,
                'discount': 5.0,
                'qty': 3.0,
                'tax_ids': [(6, 0, self.product4.taxes_id.ids)],
                'price_subtotal': 300 * (1 - 5/100.0) * 3,
                'price_subtotal_incl': 300 * (1 - 5/100.0) * 3,
            })],
            'amount_total': 1710.0,
            'amount_tax': 0.0,
            'amount_paid': 1710.0,
            'amount_return': 0.0,
        })
        self.assertEqual(
            order.week_number,
            'C', "POS order week number should be in paid C.")
        self.assertEqual(
            order.week_day,
            'Tue', "POS order week day should be in paid Tue.")
        self.assertEqual(
            order.cycle,
            'CTue', "POS order cycle should be in paid CTue.")
