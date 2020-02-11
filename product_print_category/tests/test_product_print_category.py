# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductPrintCategory(TransactionCase):
    """Tests for 'Product Print Category' Module"""

    def setUp(self):
        super(TestProductPrintCategory, self).setUp()
        self.wizard_obj = self.env["product.print.wizard"]
        # self.report_obj = self.env["report"]
        self.custom_report_obj = self.env[
            "report.product_print_category.report_pricetag"]
        self.print_category = self.env.ref(
            "product_print_category.demo_category")

    # Test Section
    def test_01_test_wizard_obsolete(self):
        wizard = self.wizard_obj.with_context(
            active_model="product.print.category",
            active_ids=[self.print_category.id], ).create({})
        self.assertEqual(
            len(wizard.line_ids),
            1,
            'Print obsolete product should propose 1 product'
        )

    def test_02_test_wizard_all(self):
        wizard = self.wizard_obj.with_context(
            active_model="product.print.category",
            active_ids=[self.print_category.id], all_products=True, ).create({
            })
        self.assertEqual(
            len(wizard.line_ids),
            2,
            "Print all products should propose 5 products"
        )
        data = wizard.print_report()
        self.env['report.product_print_category.report_pricetag'].\
            _get_report_values(docids=None, data=data.get('data'))
