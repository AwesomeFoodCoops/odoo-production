from .common import AccountInvoiceRefundOptionTest
from odoo import fields


class TestAccountInvoiceRefundOption(AccountInvoiceRefundOptionTest):

    def test_account_invoice_refund_option(self):
        """
            Test the account invoice refund option to refund only selected
            invoice line.
        """
        # Create an invoice
        invoice = self.env['account.invoice'].create(dict(
            name="Test Customer Invoice",
            payment_term_id=self.payment_term.id,
            journal_id=self.journalrec.id,
            partner_id=self.partner3.id,
            invoice_line_ids=self.invoice_line_data
        ))

        # Validate an invoice
        invoice.action_invoice_open()

        # Check invoice and invoice line
        assert invoice and invoice.invoice_line_ids

        # Create refund of selected invoice line
        invoice_refund_wizard = self.account_invoice_refund_obj.create({
            'date_invoice': fields.Datetime.today(),
            'description': 'Test Reason',
            'filter_refund': 'refund_select_product',
            'invoice_line_ids':
                [(6, 0, [invoice.invoice_line_ids.ids[0]])]
        })

        # Refund invoice
        ctx = {'active_ids': invoice.ids}
        invoice_refund_wizard.with_context(ctx).invoice_refund()

        # Check refund is created and attached to the same invoice
        assert invoice.refund_invoice_ids
