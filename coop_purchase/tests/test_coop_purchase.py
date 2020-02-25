from odoo.tests.common import TransactionCase

from odoo import fields


class TestPurchase(TransactionCase):

    def setUp(self):
        super().setUp()
        self.PurchaseOrder = self.env['purchase.order']
        self.AccountInvoice = self.env['account.invoice']
        self.AccountAccount = self.env['account.account']
        self.Journal = self.env['account.journal']
        self.supplier_id = self.env.ref('base.res_partner_3')
        self.product_1 = self.env.ref('product.product_product_8')
        self.product_1.purchase_method = 'purchase'
        self.purchase_journal = self.Journal.search(
            [('type', '=', 'purchase')], limit=1)
        self.supplier_id.default_purchase_journal_id = self.purchase_journal.id
        self.cash_journal = self.Journal.search(
            [('type', '=', 'cash')], limit=1)

        self.po_vals = {
            'partner_id': self.supplier_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_1.name,
                    'product_id': self.product_1.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_1.uom_po_id.id,
                    'price_unit': 500.0,
                    'date_planned': fields.Date.today(),
                })],
        }
        self.po = self.PurchaseOrder.create(self.po_vals)

        self.company_partner_bank = self.env['res.partner.bank'].create({
            'name': 'Test Bank',
            'partner_id': self.env.user.company_id.partner_id.id,
            'acc_number': '1234567890',
        })

    def test_001_check_po_line(self):
        self.po.order_line.update_po_price_to_vendor_price()
        vendor_price_line = self.product_1.seller_ids.filtered(
            lambda vp_line: vp_line.name.id == self.supplier_id.id)
        if vendor_price_line:
            self.assertEqual(
                vendor_price_line[0].base_price,
                self.po.order_line[0].price_unit,
                "Supplier's Base price has to be %s" %
                self.po.order_line[0].price_unit
            )

    def test_002_check_invoice(self):
        self.po.button_confirm()
        picking = self.po.picking_ids
        picking.move_line_ids.write({'qty_done': 5.0})
        picking.button_validate()

        # Vendor Bill 1
        invoice1_new = self.AccountInvoice.new({
            'purchase_id': self.po.id,
            'type': 'in_invoice',
            'company_id': self.env.user.company_id.id,
        })
        invoice1_new.purchase_order_change()
        invoice1_new._onchange_partner_id()
        invoice1_new._onchange_journal_id()
        inv_vals = invoice1_new._convert_to_write(invoice1_new._cache)
        self.invoice1 = self.AccountInvoice.create(inv_vals)
        self.assertEqual(self.invoice1.invoice_line_ids[0].quantity, 5.0,
                         "Product Quantity has to be 5.0!")
        self.invoice1.invoice_line_ids[0].quantity = 3.0
        self.invoice1.action_invoice_open()
        self.invoice1.pay_and_reconcile(self.cash_journal)

        # Vendor Bill 2
        invoice2_new = self.AccountInvoice.new({
            'purchase_id': self.po.id,
            'type': 'in_invoice',
            'company_id': self.env.user.company_id.id,
        })
        invoice2_new.purchase_order_change()
        invoice2_new._onchange_partner_id()
        invoice2_new._onchange_journal_id()
        inv2_vals = invoice2_new._convert_to_write(invoice2_new._cache)
        self.invoice2 = self.AccountInvoice.create(inv2_vals)
        self.assertEqual(self.invoice2.invoice_line_ids[0].quantity, 2.0,
                         "Product Quantity has to be 2.0!")

        # Vendor Refund Bill 3
        invoice3_new = self.AccountInvoice.new({
            'purchase_id': self.po.id,
            'type': 'in_refund',
            'company_id': self.env.user.company_id.id,
            'partner_bank_id': self.company_partner_bank.id,
        })
        invoice3_new.purchase_order_change()
        invoice3_new._onchange_partner_id()
        invoice3_new._onchange_journal_id()
        inv3_vals = invoice3_new._convert_to_write(invoice3_new._cache)
        self.invoice3 = self.AccountInvoice.create(inv3_vals)
        self.assertEqual(self.invoice3.invoice_line_ids[0].quantity, 3.0,
                         "Refund Product's Quantity has to be 3.0!")
