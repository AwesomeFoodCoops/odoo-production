# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductPrintCategory(TransactionCase):
    """Tests for 'Product Print Category' Module"""

    def setUp(self):
        super(TestProductPrintCategory, self).setUp()
        self.wizard_obj = self.env["product.print.wizard"]
        self.pricetag = self.env.ref(
            'coop_default_pricetag.pricetag_model_default'
        )
        self.custom_report_obj = self.env[
            "report.product_print_category.report_pricetag"]
        self.prod_categ = self.env.ref("product.product_category_all")
        self.prod_uom = self.env.ref("uom.product_uom_categ_unit")
        self.prod_name = self.env.ref('product.field_product_product__name')
        self.print_category = self.env['product.print.category'].create({
            'name': 'Default Category',
            'pricetag_model_id': self.pricetag.id,
            'field_ids': [(4, self.prod_name.id)],
        })
        self.template_obj = self.env['product.template']
        self.product_obj = self.env['product.product']
        self.template0 = self.template_obj.create({
            'name': 'template0',
            'categ_id': self.prod_categ.id,
            'uom_id': self.prod_uom.id,
            'uom_po_id': self.prod_uom.id,
            'description_sale': 'template0',
            'standard_price': 10.0,
            'list_price': 12.0,
            'type': 'consu',
            'print_category_id': self.print_category.id,
        })
        self.product0 = self.product_obj.create({
            'name': 'template0',
            'categ_id': self.prod_categ.id,
            'uom_id': self.prod_uom.id,
            'uom_po_id': self.prod_uom.id,
            'default_code': 'tmp0',
            'standard_price': 10.0,
            'list_price': 12.0,
            'type': 'consu',
            'product_tmpl_id': self.template0.id,
        })
        self.template1 = self.template_obj.create({
            'name': 'template1',
            'categ_id': self.prod_categ.id,
            'uom_id': self.prod_uom.id,
            'uom_po_id': self.prod_uom.id,
            'description_sale': 'template1',
            'standard_price': 50.0,
            'list_price': 60.0,
            'type': 'consu',
            'print_category_id': self.print_category.id,
        })

    # Test Section
    def test_01_test_wizard_obsolete(self):
        wizard = self.wizard_obj.with_context(
            active_model="product.print.category",
            active_ids=[self.print_category.id]).create({})
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
            3,
            "Print all products should propose 3 products"
        )
        data = wizard.print_report()
        self.env['report.coop_default_pricetag.report_pricetag'].\
            _get_report_values(docids=None, data=data.get('data'))
        self.env['report.coop_default_pricetag.report_pricetag_barcode'].\
            _get_report_values(docids=None, data=data.get('data'))
        self.env[
            'report.coop_default_pricetag.report_pricetag_simple_barcode'
        ]._get_report_values(docids=None, data=data.get('data'))
