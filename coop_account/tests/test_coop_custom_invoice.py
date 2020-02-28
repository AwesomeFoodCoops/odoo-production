from .common import CoopCustomAccountTest


class TestCoupCustomAccount(CoopCustomAccountTest):
    def test_coop_custom_account01(self):
        """
            Test the Coop Custom Account should merge the same invoice lines
            and make the required changes in memo when make the payment with
            selected operation type.
        """
        invoice_line_data = [
            (0, 0,
                {
                    'product_id': self.Product5.id,
                    'quantity': 10.0,
                    'account_id': self.Account_id.id,
                    'name': 'product test 5',
                    'price_unit': 100.00,
                }
             ),
            (0, 0,
                {
                    'product_id': self.Product5.id,
                    'quantity': 10.0,
                    'account_id': self.Account_id.id,
                    'name': 'product test 5',
                    'price_unit': 100.00,
                }
             )
        ]

        self.InvoiceAccount = self.Account.search([
            ('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)],
            limit=1)

        self.Invoice = self.AccountInvoice.create({
            'name': 'Test Customer Invoice',
            'journal_id': self.Journalrec.id,
            'partner_id': self.Partner3.id,
            'account_id': self.InvoiceAccount.id,
            'type': 'in_invoice',
            'invoice_line_ids': invoice_line_data
        })

        # Merge duplicate invoice line
        self.Invoice.merge_lines()
        assert len(self.Invoice.invoice_line_ids) == 1
