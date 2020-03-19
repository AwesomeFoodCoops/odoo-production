import time

from odoo.exceptions import ValidationError

from .common import ImprovePaymentConfirmationTest


class TestImprovePaymentConfirmation(ImprovePaymentConfirmationTest):

    def test_account_payment_confirm(self):
        """
            Test the account payment confirm improvement.
        """
        # Check invoice and invoice line
        assert self.Invoice and self.Invoice.invoice_line_ids

        # Create payment
        ctx = {'active_model': 'account.invoice',
               'active_ids': [self.Invoice.id]}
        payment = self.register_payments_model.with_context(ctx).create({
            'payment_date': time.strftime('%Y') + '-07-15',
            'journal_id': self.bank_journal_euro.id,
            'payment_method_id': self.payment.id,
            'group_invoices': True,
        })
        payment.create_payments()
        payment = self.payment_model.search([], order="id desc", limit=1)

        # Check payment posted
        self.assertEqual(payment.state, 'posted')
        # Check invoice paid
        self.assertEqual(self.Invoice.state, 'paid')

        with self.assertRaises(ValidationError):
            payment.with_context(account_payment_confirm=True).post()
