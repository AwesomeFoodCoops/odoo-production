# -*- coding: utf-8 -*-
# Copyright (C) 2015-Today: Smile (<http://www.smile.fr>)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import SavepointCase


def change_list_price_and_standard_price(products):
        for product in products:
            product.recompute_base_price()
            product.use_theoritical_price()
            product.use_theoritical_cost()


class TestProductTemplate(SavepointCase):

    def setUp(self):
        super(TestProductTemplate, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(TestProductTemplate, cls).setUpClass()
        # set up data
        product_template_env = cls.env['product.template']
        product_category_env = cls.env['product.category']
        res_partner_env = cls.env['res.partner']
        product_coefficient_env = cls.env['product.coefficient']
        product_uom_env = cls.env['product.uom']
        product_supplierinfo_env = cls.env['product.supplierinfo']
        fiscal_classification_env = \
            cls.env['account.product.fiscal.classification']

        # create products
        unit_id = product_uom_env.search([('name', 'like', 'Unit(s)')],
                                         limit=1)
        fiscla_id = \
            fiscal_classification_env.create(
                {'name': 'TEST FISCAL CLASSIFICATION'})
        cate_id = product_category_env.create({
            'name': 'Test Category',
            'type': 'normal',
            'property_cost_method': 'standard',
            'property_valuation': 'manual_periodic'})
        fixed_10 = product_coefficient_env.create({'name': 'Test Fixed 10',
                                                   'value': '10',
                                                   'operation_type': 'fixed',
                                                   'active': True})
        fixed_15 = product_coefficient_env.create({'name': 'Test Fixed 15',
                                                   'value': '15',
                                                   'operation_type': 'fixed',
                                                   'active': True})
        multiplied_20 = product_coefficient_env.create({
           'name': 'Test Multiplied 20',
           'value': '0.20',
           'operation_type': 'multiplier',
           'active': True})
        multiplied_35 = product_coefficient_env.create({
           'name': 'Test Multiplied 35',
           'value': '0.35',
           'operation_type': 'multiplier',
           'active': True})
        vendor_A = res_partner_env.create({'name': 'Vendor Test A',
                                           'supplier': True,
                                           'discount_computation': 'total',
                                           'shift_type': 'standard',
                                           'working_state': 'up_to_date'})
        vendor_B = res_partner_env.create({
           'name': 'Vendor Test B',
           'supplier': True,
           'discount_computation': 'unit_price',
           'shift_type': 'standard',
           'working_state': 'up_to_date'})

        product_A = product_template_env.create(
            {'name': 'TEST PRODUCT COEFFICIENT A',
             'list_price': 10.0,
             'standard_price': 10.0,
             'uom_id': unit_id.id,
             'uom_po_id': unit_id.id,
             'categ_id': cate_id.id,
             'alternative_base_price_sale': 0.0,
             'alternative_base_price_standard': 0.0,
             'type': 'consu',
             'fiscal_classification_id': fiscla_id.id,
             'taxes_id': False,
             'supplier_taxes_id': False,
             })
        product_B = product_template_env.create({
             'name': 'TEST PRODUCT COEFFICIENT B',
             'list_price': 15.0,
             'standard_price': 15.0,
             'uom_id': unit_id.id,
             'uom_po_id': unit_id.id,
             'categ_id': cate_id.id,
             'alternative_base_price_sale': 0.0,
             'alternative_base_price_standard': 0.0,
             'type': 'consu',
             'fiscal_classification_id': fiscla_id.id,
             'taxes_id': False,
             'supplier_taxes_id': False,
             })
        product_C = product_template_env.create({
             'name': 'TEST PRODUCT COEFFICIENT C',
             'list_price': 15.0,
             'standard_price': 15.0,
             'uom_id': unit_id.id,
             'uom_po_id': unit_id.id,
             'categ_id': cate_id.id,
             'alternative_base_price_sale': 0.0,
             'alternative_base_price_standard': 0.0,
             'type': 'consu',
             'fiscal_classification_id': fiscla_id.id,
             'taxes_id': False,
             'supplier_taxes_id': False})
        product_supplierinfo_env.create({
              'name': vendor_A.id,
              'product_tmpl_id': product_A.id,
              'delay': 1,
              'min_qty': 10000,
              'package_qty': 10000,
              'base_price': 50000,
              'price_policy': 'package',
              'discount': 0})
        product_supplierinfo_env.create({
              'name': vendor_B.id,
              'product_tmpl_id': product_A.id,
              'delay': 1,
              'min_qty': 100,
              'package_qty': 100,
              'base_price': 7.5,
              'price_policy': 'uom',
              'discount': 15})
        product_supplierinfo_env.create({
              'name': vendor_B.id,
              'product_tmpl_id': product_B.id,
              'delay': 1,
              'min_qty': 100,
              'package_qty': 100,
              'base_price': 7.5,
              'price_policy': 'uom',
              'discount': 15})
        product_supplierinfo_env.create({
              'name': vendor_A.id,
              'product_tmpl_id': product_C.id,
              'delay': 1,
              'min_qty': 10000,
              'package_qty': 10000,
              'base_price': 50000,
              'price_policy': 'package',
              'discount': 20})
        # pre-testing data
        product_A.write({'coeff1_id': fixed_10.id,
                         'coeff2_id': fixed_15.id,
                         'coeff7_id': fixed_15.id})
        product_B.write({'coeff3_id': multiplied_20.id,
                         'coeff4_id': multiplied_35.id,
                         'coeff8_id': multiplied_35.id,
                         'incl_in_standard_price_3': True,
                         'incl_in_standard_price_4': True,
                         'incl_in_standard_price_8': True})
        product_C.write({'coeff5_id': fixed_10.id,
                         'coeff6_id': multiplied_35.id,
                         'coeff9_id': fixed_15.id,
                         'incl_in_standard_price_6': True,
                         'incl_in_standard_price_9': True})
        change_list_price_and_standard_price([product_A, product_B, product_C])

    @classmethod
    def tearDownClass(cls):
        super(TestProductTemplate, cls).tearDownClass()

    def evaluate_values(self, object, expected_output):
        for exp_opt in expected_output.iteritems():
            if type(getattr(object, exp_opt[0])) == bool:
                self.assertEqual(getattr(object, exp_opt[0]),
                                 exp_opt[1])
                continue
            self.assertAlmostEqual(getattr(object, exp_opt[0]),
                                   exp_opt[1],
                                   places=4)

    def get_all_data_from_db_for_test(self):
        product_template_env = self.env['product.template']
        res_partner_env = self.env['res.partner']
        product_coefficient_env = self.env['product.coefficient']
        product_A = product_template_env.search(
            [('name', 'like', 'TEST PRODUCT COEFFICIENT A')], limit=1)
        product_B = product_template_env.search(
            [('name', 'like', 'TEST PRODUCT COEFFICIENT B')], limit=1)
        product_C = product_template_env.search(
            [('name', 'like', 'TEST PRODUCT COEFFICIENT C')], limit=1)
        fixed_10 = product_coefficient_env.search(
            [('name', 'like', 'Test Fixed 10')], limit=1)
        fixed_15 = product_coefficient_env.search(
            [('name', 'like', 'Test Fixed 15')], limit=1)
        multiplied_20 = product_coefficient_env.search(
            [('name', 'like', 'Test Multiplied 20')], limit=1)
        multiplied_35 = product_coefficient_env.search(
            [('name', 'like', 'Test Multiplied 35')], limit=1)
        vendor_A = res_partner_env.search(
            [('name', 'like', 'Vendor Test A')], limit=1)
        vendor_B = res_partner_env.search(
            [('name', 'like', 'Vendor Test B')], limit=1)
        return product_A, product_B, product_C, fixed_10, fixed_15, \
            multiplied_20, multiplied_35, vendor_A, vendor_B

    def test_checking_first_data(self):
        product_A, product_B, product_C, fixed_10, fixed_15, \
            multiplied_20, multiplied_35, vendor_A, vendor_B = \
            self.get_all_data_from_db_for_test()
        pre_test_prdA = {'name': 'TEST PRODUCT COEFFICIENT A',
                         'list_price': 45.0,
                         'standard_price': 5.0,
                         'base_price': 5.0,
                         'alternative_base_price_sale': 0.0,
                         'alternative_base_price_standard': 0.0,
                         'coeff1_inter': 15.0,
                         'coeff1_inter_sp': 5.0,
                         'coeff2_inter': 30.0,
                         'coeff2_inter_sp': 5.0,
                         'coeff7_inter': 45.0,
                         'coeff7_inter_sp': 5.0,
                         'theoritical_price': 45.0,
                         'has_theoritical_price_different': False,
                         'has_theoritical_cost_different': False}
        pre_test_prdB = {'name': 'TEST PRODUCT COEFFICIENT B',
                         'list_price': 13.95,
                         'standard_price': 13.95,
                         'base_price': 6.38,
                         'alternative_base_price_sale': 0.0,
                         'alternative_base_price_standard': 0.0,
                         'coeff3_inter': 7.656,
                         'coeff3_inter_sp': 7.656,
                         'coeff4_inter': 10.3356,
                         'coeff4_inter_sp': 10.3356,
                         'coeff8_inter': 13.95306,
                         'coeff8_inter_sp': 13.95306,
                         'theoritical_price': 13.95,
                         'has_theoritical_price_different': False,
                         'has_theoritical_cost_different': False}
        pre_test_prdC = {'name': 'TEST PRODUCT COEFFICIENT C',
                         'list_price': 33.9,
                         'standard_price': 20.4,
                         'base_price': 4.0,
                         'alternative_base_price_sale': 0.0,
                         'alternative_base_price_standard': 0.0,
                         'coeff5_inter': 14.0,
                         'coeff5_inter_sp': 4.0,
                         'coeff6_inter': 18.9,
                         'coeff6_inter_sp': 5.4,
                         'coeff9_inter': 33.9,
                         'coeff9_inter_sp': 20.4,
                         'theoritical_price': 33.9,
                         'has_theoritical_price_different': False,
                         'has_theoritical_cost_different': False}
        self.evaluate_values(product_A, pre_test_prdA)
        self.evaluate_values(product_B, pre_test_prdB)
        self.evaluate_values(product_C, pre_test_prdC)

    def test_base_price_changed_make_all_price_changed(self):
        """Checks that Base price changed makes theorical price
         * and theorical standard price changed.
        """
        product_A, product_B, product_C, fixed_10, fixed_15, \
            multiplied_20, multiplied_35, vendor_A, vendor_B = \
            self.get_all_data_from_db_for_test()

        # testing
        # case change base_price and discount
        product_A.write({'seller_ids': [(1, product_A.seller_ids[0].id,
                                        {'base_price': 70000,
                                         'discount': 10, })]})
        # case change only base_price
        product_B.write({'seller_ids': [(1, product_B.seller_ids[0].id,
                                        {'base_price': 8.0,
                                         'discount': 15, })]})
        # case change only discount
        product_C.write({'seller_ids': [(1, product_C.seller_ids[0].id,
                                        {'base_price': 50000,
                                         'discount': 0, })]})
        # expected output
        expected_ouput_prdA = {'base_price': 6.3,
                               'has_theoritical_price_different': True,
                               'has_theoritical_cost_different': True}
        expected_ouput_prdB = {'base_price': 6.8,
                               'has_theoritical_price_different': True,
                               'has_theoritical_cost_different': True}
        expected_ouput_prdC = {'base_price': 5.0,
                               'has_theoritical_price_different': True,
                               'has_theoritical_cost_different': True}
        # check change base price
        self.evaluate_values(product_A, expected_ouput_prdA)
        self.evaluate_values(product_B, expected_ouput_prdB)
        self.evaluate_values(product_C, expected_ouput_prdC)

        # change list price and standard price
        change_list_price_and_standard_price([product_A,
                                              product_B,
                                              product_C])
        expected_ouput_prdA.update({
            'list_price': 46.3,
            'standard_price': 6.3,
            'has_theoritical_price_different': False,
            'has_theoritical_cost_different': False})
        expected_ouput_prdB.update({
            'list_price': 14.87,
            'standard_price': 14.87,
            'has_theoritical_price_different': False,
            'has_theoritical_cost_different': False})
        expected_ouput_prdC.update({
            'list_price': 35.25,
            'standard_price': 21.75,
            'has_theoritical_price_different': False,
            'has_theoritical_cost_different': False})

        # check values
        self.evaluate_values(product_A, expected_ouput_prdA)
        self.evaluate_values(product_B, expected_ouput_prdB)
        self.evaluate_values(product_C, expected_ouput_prdC)

    def test_base_price_changes_doesnt_make_any_price_changed(self):
        """Checks that Base price changed doesn't make theorical price
         * and theorical standard price changed.
        """
        product_A, product_B, product_C, fixed_10, fixed_15, \
            multiplied_20, multiplied_35, vendor_A, vendor_B = \
            self.get_all_data_from_db_for_test()

        # testing
        product_A.write({'seller_ids': [(1, product_A.seller_ids[0].id,
                                         {'discount': 0, })],
                         'alternative_base_price_sale': 10.0,
                         'alternative_base_price_standard': 10.0})
        product_B.write({'seller_ids': [(1, product_B.seller_ids[0].id,
                                         {'discount': 0, })],
                         'alternative_base_price_sale': 10.0,
                         'alternative_base_price_standard': 10.0})
        product_C.write({'seller_ids': [(1, product_C.seller_ids[0].id,
                                         {'discount': 0, })],
                         'alternative_base_price_sale': 10.0,
                         'alternative_base_price_standard': 10.0})
        # expected output
        expected_ouput_prdA = {'base_price': 5.0,
                               'alternative_base_price_sale': 10.0,
                               'alternative_base_price_standard': 10.0,
                               'has_theoritical_price_different': True,
                               'has_theoritical_cost_different': True}
        expected_ouput_prdB = {'base_price': 7.5,
                               'alternative_base_price_sale': 10.0,
                               'alternative_base_price_standard': 10.0,
                               'has_theoritical_price_different': True,
                               'has_theoritical_cost_different': True}
        expected_ouput_prdC = {'base_price': 5.0,
                               'alternative_base_price_sale': 10.0,
                               'alternative_base_price_standard': 10.0,
                               'has_theoritical_price_different': True,
                               'has_theoritical_cost_different': True}
        # check change base price
        self.evaluate_values(product_A, expected_ouput_prdA)
        self.evaluate_values(product_B, expected_ouput_prdB)
        self.evaluate_values(product_C, expected_ouput_prdC)

        # change list price and standard price
        change_list_price_and_standard_price([product_A, product_B, product_C])
        expected_ouput_prdA.update({
            'list_price': 50,
            'standard_price': 10.0,
            'has_theoritical_price_different': False,
            'has_theoritical_cost_different': False})
        expected_ouput_prdB.update({
            'list_price': 21.87,
            'standard_price': 21.87,
            'has_theoritical_price_different': False,
            'has_theoritical_cost_different': False})
        expected_ouput_prdC.update({
            'list_price': 42,
            'standard_price': 28.5,
            'has_theoritical_price_different': False,
            'has_theoritical_cost_different': False})

        # check values
        self.evaluate_values(product_A, expected_ouput_prdA)
        self.evaluate_values(product_B, expected_ouput_prdB)
        self.evaluate_values(product_C, expected_ouput_prdC)

    def test_no_coefficient_included_in_standard_price(self):
        product_A, product_B, product_C, fixed_10, fixed_15, \
            multiplied_20, multiplied_35, vendor_A, vendor_B = \
            self.get_all_data_from_db_for_test()

        # testing
        # case change base_price and discount
        product_A.write({'seller_ids': [(1, product_A.seller_ids[0].id,
                                        {'base_price': 70000,
                                         'discount': 10, })],
                         'coeff1_id': fixed_10.id,  # 16.3
                         'coeff2_id': fixed_15.id,  # 31.3
                         'coeff3_id': multiplied_35.id,  # 42.255
                         'coeff4_id': multiplied_20.id,  # 50.706
                         'coeff5_id': fixed_15.id,  # 65.706
                         'coeff6_id': fixed_10.id,  # 75.706
                         'coeff7_id': multiplied_20.id,  # 90.8472
                         'coeff8_id': fixed_15.id,  # 105.88472
                         'coeff9_id': multiplied_20.id})  # 127.02
        # expected output
        expected_ouput_prdA = {'base_price': 6.3,
                               'coeff1_inter': 16.3,
                               'coeff1_inter_sp': 6.3,
                               'coeff2_inter': 31.3,
                               'coeff2_inter_sp': 6.3,
                               'coeff3_inter': 42.255,
                               'coeff3_inter_sp': 6.3,
                               'coeff4_inter': 50.706,
                               'coeff4_inter_sp': 6.3,
                               'coeff5_inter': 65.706,
                               'coeff5_inter_sp': 6.3,
                               'coeff6_inter': 75.706,
                               'coeff6_inter_sp': 6.3,
                               'coeff7_inter': 90.8472,
                               'coeff7_inter_sp': 6.3,
                               'coeff8_inter': 105.8472,
                               'coeff8_inter_sp': 6.3,
                               'coeff9_inter': 127.02,
                               'coeff9_inter_sp': 6.3,
                               'theoritical_price': 127.02,
                               'has_theoritical_price_different': True,
                               'has_theoritical_cost_different': True}
        # check change base price
        self.evaluate_values(product_A, expected_ouput_prdA)

        # change list price and standard price
        change_list_price_and_standard_price([product_A])
        expected_ouput_prdA.update({
            'base_price': 6.3,
            'list_price': 127.02,
            'standard_price': 6.3,
            'has_theoritical_price_different': False,
            'has_theoritical_cost_different': False})

        # check values
        self.evaluate_values(product_A, expected_ouput_prdA)

    def test_discount_make_base_price_changed(self):
        product_A, product_B, product_C, fixed_10, fixed_15, \
            multiplied_20, multiplied_35, vendor_A, vendor_B = \
            self.get_all_data_from_db_for_test()

        # testing
        # case change base_price and discount
        product_A.write({'seller_ids': [(1, product_A.seller_ids[0].id,
                                        {'base_price': 50000,
                                         'discount': 10, })]})
        # expected output
        expected_ouput_prdA = {'base_price': 4.5,
                               'list_price': 45.0,
                               'standard_price': 5.0,
                               'coeff1_inter': 14.5,
                               'coeff1_inter_sp': 4.5,
                               'coeff2_inter': 29.5,
                               'coeff2_inter_sp': 4.5,
                               'coeff3_inter': 29.5,
                               'coeff3_inter_sp': 4.5,
                               'coeff4_inter': 29.5,
                               'coeff4_inter_sp': 4.5,
                               'coeff5_inter': 29.5,
                               'coeff5_inter_sp': 4.5,
                               'coeff6_inter': 29.5,
                               'coeff6_inter_sp': 4.5,
                               'coeff7_inter': 44.5,
                               'coeff7_inter_sp': 4.5,
                               'coeff8_inter': 44.5,
                               'coeff8_inter_sp': 4.5,
                               'coeff9_inter': 44.5,
                               'coeff9_inter_sp': 4.5,
                               'theoritical_price': 44.5,
                               'has_theoritical_price_different': True,
                               'has_theoritical_cost_different': True}
        # check change base price
        self.evaluate_values(product_A, expected_ouput_prdA)

        # change list price and standard price
        change_list_price_and_standard_price([product_A])
        expected_ouput_prdA.update({
            'base_price': 4.5,
            'list_price': 44.5,
            'standard_price': 4.5,
            'has_theoritical_price_different': False,
            'has_theoritical_cost_different': False})

        # check values
        self.evaluate_values(product_A, expected_ouput_prdA)

    def test_discount_doesnt_make_base_price_changed(self):
        product_A, product_B, product_C, fixed_10, fixed_15, \
            multiplied_20, multiplied_35, vendor_A, vendor_B = \
            self.get_all_data_from_db_for_test()

        # testing
        # case change base_price and discount and discount is 0 (doesn't take
        # effect on base_price)
        product_A.write({'seller_ids': [(1, product_A.seller_ids[0].id,
                                        {'base_price': 70000,
                                         'discount': 0, })]})
        # expected output
        expected_ouput_prdA = {'base_price': 7.0,
                               'list_price': 45.0,
                               'standard_price': 5.0,
                               'coeff1_inter': 17.0,
                               'coeff1_inter_sp': 7.0,
                               'coeff2_inter': 32.0,
                               'coeff2_inter_sp': 7.0,
                               'coeff3_inter': 32.0,
                               'coeff3_inter_sp': 7.0,
                               'coeff4_inter': 32.0,
                               'coeff4_inter_sp': 7.0,
                               'coeff5_inter': 32.0,
                               'coeff5_inter_sp': 7.0,
                               'coeff6_inter': 32.0,
                               'coeff6_inter_sp': 7.0,
                               'coeff7_inter': 47.0,
                               'coeff7_inter_sp': 7.0,
                               'coeff8_inter': 47.0,
                               'coeff8_inter_sp': 7.0,
                               'coeff9_inter': 47.0,
                               'coeff9_inter_sp': 7.0,
                               'theoritical_price': 47.0,
                               'has_theoritical_price_different': True,
                               'has_theoritical_cost_different': True}
        # check change base price
        self.evaluate_values(product_A, expected_ouput_prdA)

        # change list price and standard price
        change_list_price_and_standard_price([product_A])
        expected_ouput_prdA.update({
            'base_price': 7.0,
            'list_price': 47.0,
            'standard_price': 7.0,
            'has_theoritical_price_different': False,
            'has_theoritical_cost_different': False})

        # check values
        self.evaluate_values(product_A, expected_ouput_prdA)
