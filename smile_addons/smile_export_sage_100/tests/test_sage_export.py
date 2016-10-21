# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 GreenBiz
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime

from openerp.tests.common import TransactionCase
from openerp.exceptions import except_orm


class TestSageExport(TransactionCase):

    def setUp(self):
        super(TestSageExport, self).setUp()

        self.account_inv = self.env['account.invoice']
        self.account_inv_line = self.env['account.invoice.line']
        self.res_partner = self.env['res.partner']
        self.sage_export = self.env['smile.export.sage']

        company_id = self.env.ref('base.main_company')
        currency_id = self.env.ref('base.EUR')
        self.journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        a_rec_id = self.env.ref('.401100')
        acc_purchase_id = self.env.ref('.607100')

        self.product_id = self.env['product.product'].search([('purchase_ok', '=', True)], limit=1)

        self.today = datetime.now().date()

        # Create Supplier
        vals = {'name': 'Supplier',
                'supplier': True}
        self.supplier = self.res_partner.create(vals)

        # Create Invoice
        inv_vals = {'partner_id': self.supplier.id,
                    'journal_id': self.journal_id.id,
                    'company_id': company_id.id,
                    'currency_id': currency_id.id,
                    'account_id': a_rec_id.id,
                    'date_invoice': self.today,
                    'type': 'in_invoice'}
        self.inv_id = self.account_inv.create(inv_vals)

        inv_line_vals = {'product_id': self.product_id.id,
                         'account_id': acc_purchase_id.id,
                         'name': 'Product Demo',
                         'price_unit': 100,
                         'quantity': 2,
                         'invoice_id': self.inv_id.id}
        self.account_inv_line.create(inv_line_vals)

        # Create Export
        export_vals = {'date_from': self.today,
                       'date_to': self.today}
        self.sage_export_id = self.sage_export.create(export_vals)

    def test_sage_export_fail_config_problem(self):
        """
            1. I Validate the invoice
            2. I can not create sage report...config problem
        """
        self.inv_id.signal_workflow('invoice_open')
        self.assertTrue(self.inv_id.state == 'open')
        with self.assertRaises(except_orm):
            self.sage_export_id.create_report()

    def test_sage_export_succeded(self):
        """
            1. I Validate the invoice
            2. I configure journal & supplier sage code
            3. I export report
            4. I can not export report for second time...no move lines found
        """
        self.inv_id.signal_workflow('invoice_open')
        self.assertTrue(self.inv_id.state == 'open')
        self.journal_id.sage_code = 'BC'
        self.supplier.property_account_payable_sage = '40122585'
        export_ok = self.sage_export_id.create_report()
        self.assertTrue(export_ok)
        with self.assertRaises(except_orm):
            self.sage_export_id.create_report()
