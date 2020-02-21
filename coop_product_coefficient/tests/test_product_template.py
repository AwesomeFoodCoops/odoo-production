from odoo.tests.common import SavepointCase


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
        product_template_env = cls.env["product.template"]
        product_category_env = cls.env["product.category"]
        res_partner_env = cls.env["res.partner"]
        product_coefficient_env = cls.env["product.coefficient"]
        product_uom_env = cls.env["uom.uom"]
        product_supplierinfo_env = cls.env["product.supplierinfo"]
        unit_id = product_uom_env.search(
            [("name", "like", "Unit(s)")], limit=1
        )
        cate_id = product_category_env.create({
            "name": "Test Category",
            "property_cost_method": "standard",
            "property_valuation": "manual_periodic",
        })
        fixed_10 = product_coefficient_env.create({
            "name": "Test Fixed 10",
            "value": "10",
            "operation_type": "fixed",
            "active": True,
        })
        fixed_15 = product_coefficient_env.create({
            "name": "Test Fixed 15",
            "value": "15",
            "operation_type": "fixed",
            "active": True,
        })
        multiplied_20 = product_coefficient_env.create({
            "name": "Test Multiplied 20",
            "value": "0.20",
            "operation_type": "multiplier",
            "active": True,
        })
        multiplied_35 = product_coefficient_env.create({
            "name": "Test Multiplied 35",
            "value": "0.35",
            "operation_type": "multiplier",
            "active": True,
        })
        vendor_a = res_partner_env.create({
            "name": "Vendor Test A",
            "supplier": True,
            "shift_type": "standard",
            "working_state": "up_to_date",
        })
        vendor_b = res_partner_env.create({
            "name": "Vendor Test B",
            "supplier": True,
            "shift_type": "standard",
            "working_state": "up_to_date",
        })

        product_a = product_template_env.create({
            "name": "TEST PRODUCT COEFFICIENT A",
            "list_price": 10.0,
            "standard_price": 10.0,
            "uom_id": unit_id.id,
            "uom_po_id": unit_id.id,
            "categ_id": cate_id.id,
            "alternative_base_price_sale": 0.0,
            "alternative_base_price_standard": 0.0,
            "type": "consu",
            "taxes_id": False,
            "supplier_taxes_id": False,
        })
        product_b = product_template_env.create({
            "name": "TEST PRODUCT COEFFICIENT B",
            "list_price": 15.0,
            "standard_price": 15.0,
            "uom_id": unit_id.id,
            "uom_po_id": unit_id.id,
            "categ_id": cate_id.id,
            "alternative_base_price_sale": 0.0,
            "alternative_base_price_standard": 0.0,
            "type": "consu",
            "taxes_id": False,
            "supplier_taxes_id": False,
        })
        product_c = product_template_env.create({
            "name": "TEST PRODUCT COEFFICIENT C",
            "list_price": 15.0,
            "standard_price": 15.0,
            "uom_id": unit_id.id,
            "uom_po_id": unit_id.id,
            "categ_id": cate_id.id,
            "alternative_base_price_sale": 0.0,
            "alternative_base_price_standard": 0.0,
            "type": "consu",
            "taxes_id": False,
            "supplier_taxes_id": False,
        })
        product_supplierinfo_env.create({
            "name": vendor_a.id,
            "product_tmpl_id": product_a.id,
            "delay": 1,
            "min_qty": 10000,
            "price": 5.0,
            "discount": 0,
        })
        product_supplierinfo_env.create({
            "name": vendor_b.id,
            "product_tmpl_id": product_a.id,
            "delay": 1,
            "min_qty": 100,
            "price": 7.5,
            "discount": 15,
        })
        product_supplierinfo_env.create({
            "name": vendor_b.id,
            "product_tmpl_id": product_b.id,
            "delay": 1,
            "min_qty": 100,
            "price": 7.5,
            "discount": 15,
        })
        product_supplierinfo_env.create({
            "name": vendor_a.id,
            "product_tmpl_id": product_c.id,
            "delay": 1,
            "min_qty": 10000,
            "price": 50000,
            "discount": 20,
        })
        # pre-testing data
        product_a.write({
            "coeff1_id": fixed_10.id,
            "coeff2_id": fixed_15.id,
            "coeff7_id": fixed_15.id,
        })
        product_b.write({
            "coeff3_id": multiplied_20.id,
            "coeff4_id": multiplied_35.id,
            "coeff8_id": multiplied_35.id,
            "incl_in_standard_price_3": True,
            "incl_in_standard_price_4": True,
            "incl_in_standard_price_8": True,
        })
        product_c.write({
            "coeff5_id": fixed_10.id,
            "coeff6_id": multiplied_35.id,
            "coeff9_id": fixed_15.id,
            "incl_in_standard_price_6": True,
            "incl_in_standard_price_9": True,
        })
        change_list_price_and_standard_price([
            product_a,
            product_b,
            product_c
        ])
        cls.product_a = product_template_env.search(
            [("name", "like", "TEST PRODUCT COEFFICIENT A")], limit=1
        )
        cls.product_b = product_template_env.search(
            [("name", "like", "TEST PRODUCT COEFFICIENT B")], limit=1
        )
        cls.product_c = product_template_env.search(
            [("name", "like", "TEST PRODUCT COEFFICIENT C")], limit=1
        )
        cls.fixed_10 = product_coefficient_env.search(
            [("name", "like", "Test Fixed 10")], limit=1
        )
        cls.fixed_15 = product_coefficient_env.search(
            [("name", "like", "Test Fixed 15")], limit=1
        )
        cls.multiplied_20 = product_coefficient_env.search(
            [("name", "like", "Test Multiplied 20")], limit=1
        )
        cls.multiplied_35 = product_coefficient_env.search(
            [("name", "like", "Test Multiplied 35")], limit=1
        )
        cls.vendor_a = res_partner_env.search(
            [("name", "like", "Vendor Test A")], limit=1
        )
        cls.vendor_b = res_partner_env.search(
            [("name", "like", "Vendor Test B")], limit=1
        )

    @classmethod
    def tearDownClass(cls):
        return super(TestProductTemplate, cls).tearDownClass()

    def evaluate_values(self, product, expected_output):
        for exp_opt in expected_output.items():
            if type(getattr(product, exp_opt[0])) == bool:
                self.assertEqual(getattr(product, exp_opt[0]), exp_opt[1])
                continue
            self.assertAlmostEqual(
                getattr(product, exp_opt[0]), exp_opt[1], places=4
            )

    def test_checking_first_data(self):
        pre_test_prdA = {
            "name": "TEST PRODUCT COEFFICIENT A",
            "list_price": 45.0,
            "standard_price": 5.0,
            "base_price": 5.0,
            "alternative_base_price_sale": 0.0,
            "alternative_base_price_standard": 0.0,
            "coeff1_inter": 15.0,
            "coeff1_inter_sp": 5.0,
            "coeff2_inter": 30.0,
            "coeff2_inter_sp": 5.0,
            "coeff7_inter": 45.0,
            "coeff7_inter_sp": 5.0,
            "theoritical_price": 45.0,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        }
        pre_test_prdB = {
            "name": "TEST PRODUCT COEFFICIENT B",
            "list_price": 13.95,
            "standard_price": 13.95,
            "base_price": 6.38,
            "alternative_base_price_sale": 0.0,
            "alternative_base_price_standard": 0.0,
            "coeff3_inter": 7.656,
            "coeff3_inter_sp": 7.656,
            "coeff4_inter": 10.3356,
            "coeff4_inter_sp": 10.3356,
            "coeff8_inter": 13.95306,
            "coeff8_inter_sp": 13.95306,
            "theoritical_price": 13.95,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": True,
        }
        pre_test_prdC = {
            "name": "TEST PRODUCT COEFFICIENT C",
            "list_price": 54028.5,
            "standard_price": 54015.0,
            "base_price": 40000.0,
            "alternative_base_price_sale": 0.0,
            "alternative_base_price_standard": 0.0,
            "coeff5_inter": 40010.0,
            "coeff5_inter_sp": 40000.0,
            "coeff6_inter": 54013.5,
            "coeff6_inter_sp": 54000.0,
            "coeff9_inter": 54028.5,
            "coeff9_inter_sp": 54015.0,
            "theoritical_price": 54028.5,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        }
        self.evaluate_values(self.product_a, pre_test_prdA)
        self.evaluate_values(self.product_b, pre_test_prdB)
        self.evaluate_values(self.product_c, pre_test_prdC)

    def test_base_price_changed_make_all_price_changed(self):
        """Checks that Base price changed makes theorical price
         * and theorical standard price changed.
        """
        # testing
        # case change base_price and discount
        self.product_a.write({
            "coeff5_inter_sp": 6.3,
            "seller_ids": [(
                1,
                self.product_a.seller_ids[0].id,
                {"price": 70000, "discount": 10},
            )]
        })
        # case change only base_price
        self.product_b.write({
            "seller_ids": [(
                1,
                self.product_b.seller_ids[0].id,
                {"price": 8.0, "discount": 15},
            )]
        })
        # case change only discount
        self.product_c.write({
            "seller_ids": [(
                1,
                self.product_c.seller_ids[0].id,
                {"price": 50000, "discount": 0},
            )]
        })
        # expected output
        expected_ouput_prda = {
            "base_price": 63000,
            "has_theoritical_price_different": True,
            "has_theoritical_cost_different": True,
        }
        expected_ouput_prdB = {
            "base_price": 6.8,
            "has_theoritical_price_different": True,
            "has_theoritical_cost_different": True,
        }
        expected_ouput_prdC = {
            "base_price": 50000,
            "has_theoritical_price_different": True,
            "has_theoritical_cost_different": True,
        }
        # check change base price
        self.evaluate_values(self.product_a, expected_ouput_prda)
        self.evaluate_values(self.product_b, expected_ouput_prdB)
        self.evaluate_values(self.product_c, expected_ouput_prdC)
        # change list price and standard price
        change_list_price_and_standard_price([self.product_a, self.product_b,
                                              self.product_c])
        expected_ouput_prda.update({
            "list_price": 63040.0,
            "standard_price": 63000.0,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        })
        expected_ouput_prdB.update({
            "list_price": 14.87,
            "standard_price": 14.87,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": True,
        })
        expected_ouput_prdC.update({
            "list_price": 67528.5,
            "standard_price": 67515.0,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        })
        # check values
        self.evaluate_values(self.product_a, expected_ouput_prda)
        self.evaluate_values(self.product_b, expected_ouput_prdB)
        self.evaluate_values(self.product_c, expected_ouput_prdC)

    def test_base_price_changes_doesnt_make_any_price_changed(self):
        """Checks that Base price changed doesn't make theorical price
         * and theorical standard price changed.
        """
        # testing
        self.product_a.write({
            "seller_ids": [
                (1, self.product_a.seller_ids[0].id, {"discount": 0})
            ],
            "alternative_base_price_sale": 10.0,
            "alternative_base_price_standard": 10.0,
        })
        self.product_b.write({
            "seller_ids": [
                (1, self.product_b.seller_ids[0].id, {"discount": 0})
            ],
            "alternative_base_price_sale": 10.0,
            "alternative_base_price_standard": 10.0,
        })
        self.product_c.write({
            "seller_ids": [
                (1, self.product_c.seller_ids[0].id, {"discount": 0})
            ],
            "alternative_base_price_sale": 10.0,
            "alternative_base_price_standard": 10.0,
        })
        # expected output
        expected_ouput_prda = {
            "base_price": 5.0,
            "alternative_base_price_sale": 10.0,
            "alternative_base_price_standard": 10.0,
            "has_theoritical_price_different": True,
            "has_theoritical_cost_different": True,
        }
        expected_ouput_prdB = {
            "base_price": 7.5,
            "alternative_base_price_sale": 10.0,
            "alternative_base_price_standard": 10.0,
            "has_theoritical_price_different": True,
            "has_theoritical_cost_different": True,
        }
        expected_ouput_prdC = {
            "base_price": 50000.0,
            "alternative_base_price_sale": 10.0,
            "alternative_base_price_standard": 10.0,
            "has_theoritical_price_different": True,
            "has_theoritical_cost_different": True,
        }
        # check change base price
        self.evaluate_values(self.product_a, expected_ouput_prda)
        self.evaluate_values(self.product_b, expected_ouput_prdB)
        self.evaluate_values(self.product_c, expected_ouput_prdC)
        # change list price and standard price
        change_list_price_and_standard_price([self.product_a, self.product_b,
                                              self.product_c])
        expected_ouput_prda.update({
            "list_price": 50,
            "standard_price": 10.0,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        })
        expected_ouput_prdB.update({
            "list_price": 21.87,
            "standard_price": 21.87,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        })
        expected_ouput_prdC.update({
            "list_price": 42,
            "standard_price": 28.5,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        })
        # check values
        self.evaluate_values(self.product_a, expected_ouput_prda)
        self.evaluate_values(self.product_b, expected_ouput_prdB)
        self.evaluate_values(self.product_c, expected_ouput_prdC)

    def test_no_coefficient_included_in_standard_price(self):
        # testing
        # case change base_price and discount
        self.product_a.write({
            "seller_ids": [(
                1,
                self.product_a.seller_ids[0].id,
                {"price": 70000, "discount": 10},
            )],
            "coeff1_id": self.fixed_10.id,  # 16.3
            "coeff2_id": self.fixed_15.id,  # 31.3
            "coeff3_id": self.multiplied_35.id,  # 42.255
            "coeff4_id": self.multiplied_20.id,  # 50.706
            "coeff5_id": self.fixed_15.id,  # 65.706
            "coeff6_id": self.fixed_10.id,  # 75.706
            "coeff7_id": self.multiplied_20.id,  # 90.8472
            "coeff8_id": self.fixed_15.id,  # 105.88472
            "coeff9_id": self.multiplied_20.id,
        })
        # expected output
        expected_ouput_prda = {
            "base_price": 63000.0,
            "coeff1_inter": 63010.0,
            "coeff1_inter_sp": 63000,
            "coeff2_inter": 63025.0,
            "coeff2_inter_sp": 63000.0,
            "coeff3_inter": 85083.75,
            "coeff3_inter_sp": 63000.0,
            "coeff4_inter": 102100.5,
            "coeff4_inter_sp": 63000.0,
            "coeff5_inter": 102115.5,
            "coeff5_inter_sp": 63000.0,
            "coeff6_inter": 102125.5,
            "coeff6_inter_sp": 63000.0,
            "coeff7_inter": 122550.6,
            "coeff7_inter_sp": 63000.0,
            "coeff8_inter": 122565.6,
            "coeff8_inter_sp": 63000.0,
            "coeff9_inter": 147078.72,
            "coeff9_inter_sp": 63000.0,
            "theoritical_price": 147078.72,
            "has_theoritical_price_different": True,
            "has_theoritical_cost_different": True,
        }
        # check change base price
        self.evaluate_values(self.product_a, expected_ouput_prda)
        # change list price and standard price
        change_list_price_and_standard_price([self.product_a])
        expected_ouput_prda.update({
            "base_price": 63000.0,
            "list_price": 147078.72,
            "standard_price": 63000.0,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        })
        # check values
        self.evaluate_values(self.product_a, expected_ouput_prda)

    def test_discount_make_base_price_changed(self):
        # testing
        # case change base_price and discount
        self.product_a.write({
            "seller_ids": [(
                1,
                self.product_a.seller_ids[0].id,
                {"price": 5, "discount": 10},
            )]
        })
        # expected output
        expected_ouput_prda = {
            "base_price": 4.5,
            "list_price": 45.0,
            "standard_price": 5.0,
            "coeff1_inter": 14.5,
            "coeff1_inter_sp": 4.5,
            "coeff2_inter": 29.5,
            "coeff2_inter_sp": 4.5,
            "coeff3_inter": 29.5,
            "coeff3_inter_sp": 4.5,
            "coeff4_inter": 29.5,
            "coeff4_inter_sp": 4.5,
            "coeff5_inter": 29.5,
            "coeff5_inter_sp": 4.5,
            "coeff6_inter": 29.5,
            "coeff6_inter_sp": 4.5,
            "coeff7_inter": 44.5,
            "coeff7_inter_sp": 4.5,
            "coeff8_inter": 44.5,
            "coeff8_inter_sp": 4.5,
            "coeff9_inter": 44.5,
            "coeff9_inter_sp": 4.5,
            "theoritical_price": 44.5,
            "has_theoritical_price_different": True,
            "has_theoritical_cost_different": True,
        }
        # check change base price
        self.evaluate_values(self.product_a, expected_ouput_prda)
        # change list price and standard price
        change_list_price_and_standard_price([self.product_a])
        expected_ouput_prda.update({
            "base_price": 4.5,
            "list_price": 44.5,
            "standard_price": 4.5,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        })
        # check values
        self.evaluate_values(self.product_a, expected_ouput_prda)

    def test_discount_doesnt_make_base_price_changed(self):
        # testing
        # case change base_price and discount and discount is 0 (doesn't take
        # effect on base_price)
        self.product_a.write({
            "seller_ids": [(
                1,
                self.product_a.seller_ids[0].id,
                {"price": 70000, "discount": 0},
            )]
        })
        # expected output
        expected_ouput_prda = {
            "base_price": 70000.0,
            "list_price": 45.0,
            "standard_price": 5.0,
            "coeff1_inter": 70010.0,
            "coeff1_inter_sp": 70000.0,
            "coeff2_inter": 70025.0,
            "coeff2_inter_sp": 70000.0,
            "coeff3_inter": 70025.0,
            "coeff3_inter_sp": 70000.0,
            "coeff4_inter": 70025.0,
            "coeff4_inter_sp": 70000.0,
            "coeff5_inter": 70025.0,
            "coeff5_inter_sp": 70000.0,
            "coeff6_inter": 70025.0,
            "coeff6_inter_sp": 70000.0,
            "coeff7_inter": 70040.0,
            "coeff7_inter_sp": 70000.0,
            "coeff8_inter": 70040.0,
            "coeff8_inter_sp": 70000.0,
            "coeff9_inter": 70040.0,
            "coeff9_inter_sp": 70000.0,
            "theoritical_price": 70040.0,
            "has_theoritical_price_different": True,
            "has_theoritical_cost_different": True,
        }
        # check change base price
        self.evaluate_values(self.product_a, expected_ouput_prda)
        # change list price and standard price
        change_list_price_and_standard_price([self.product_a])
        expected_ouput_prda.update({
            "base_price": 70000.0,
            "list_price": 70040.0,
            "standard_price": 70000.0,
            "has_theoritical_price_different": False,
            "has_theoritical_cost_different": False,
        })
        # check values
        self.evaluate_values(self.product_a, expected_ouput_prda)
