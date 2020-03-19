from .common import AccountInvoiceRefundOptionTest
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestAccountInvoiceRefundOption(AccountInvoiceRefundOptionTest):

    def test_account_invoice_refund_option(self):
        """
            Test the account invoice refund option to refund only selected
            invoice line.
        """
        # Check invoice and invoice line
        assert self.Invoice and self.Invoice.invoice_line_ids

        # Create refund of selected invoice line
        invoice_refund_wizard = self.account_invoice_refund_obj.create({
            'date_invoice': datetime.today().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
            'description': 'Test Reason',
            'filter_refund': 'refund_select_product',
            'invoice_line_ids':
                [(6, 0, [self.Invoice.invoice_line_ids.ids[0]])]
        })

        # Refund invoice
        ctx = {'active_ids': self.Invoice.ids}
        invoice_refund_wizard.with_context(ctx).invoice_refund()

        # Check refund is created and attached to the same invoice
        assert self.Invoice.refund_invoice_ids
