# -*- coding: utf-8 -*-
# © 2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.tests.common as common


class TestAbstractSettings(common.TransactionCase):

    def setUp(self):
        super(TestAbstractSettings, self).setUp()
        self.partner_id = self.ref('base.res_partner_12')
        self.company = self.env.ref('base.main_company')

    def test_config(self):
        wiz = self.env['a.config.settings'].create({})
        wiz.name = 'Toto'
        wiz.integer = 11
        wiz.partner_id = self.partner_id
        wiz.execute()

        self.assertEqual(self.company.prefix_a_name, wiz.name)
        self.assertEqual(self.company.prefix_a_integer, wiz.integer)
        self.assertEqual(self.company.prefix_a_partner_id, wiz.partner_id)

    def test_config_old_api(self):
        wiz = self.env['b.config.settings'].create({})
        wiz.name = 'Toto'
        wiz.integer = 11
        wiz.partner_id = self.partner_id
        wiz.execute()

        self.assertEqual(self.company.prefix_b_name, wiz.name)
        self.assertEqual(self.company.prefix_b_integer, wiz.integer)
        self.assertEqual(self.company.prefix_b_partner_id, wiz.partner_id)
