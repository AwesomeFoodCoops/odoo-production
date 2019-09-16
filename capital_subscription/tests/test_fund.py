from .common import CapitalSubscriptionTest


class TestFund(CapitalSubscriptionTest):
    def test_capital_fundraising_confirm_payment01(self):
        """
            Test the Capital Fundraising with Payment Confirm True , it should create Invoice and
            Invoice Status must be Paid
        """
        wiz = self.CapitalFund.create({
            'date_invoice': self.date_invoice,
            'partner_id': self.partner_agrolite_id,
            'category_id': self.category_id,
            'share_qty': self.share_qty,
            'payment_journal_id': self.payment_journal_id,
            'confirm_payment': True,
            'payment_term_id': self.payment_term_id
        })

        invoice_dict = wiz.button_confirm()
        invoice = self.env[invoice_dict['res_model']].browse(
            invoice_dict['res_id'])
        self.assertEqual(invoice.is_capital_fundraising, 1)
        self.assertEqual(invoice.fundraising_category_id.id, self.category_id)
        self.assertEqual(invoice.invoice_line_ids[0].quantity, self.share_qty)
        self.assertEqual(invoice.state, 'paid')

    def test_capital_fundraising_confirm_payment02(self):
        """
            Test the Capital Fundraising with Payment Confirm False, it should create Invoice and
            Invoice Status must be Open
        """
        wiz = self.CapitalFund.create({
            'date_invoice': self.date_invoice,
            'partner_id': self.partner_agrolite_id,
            'category_id': self.category_id,
            'share_qty': self.share_qty,
            'payment_journal_id': self.payment_journal_id,
            'confirm_payment': False,
            'payment_term_id': self.payment_term_id
        })

        invoice_dict = wiz.button_confirm()
        invoice = self.env[invoice_dict['res_model']].browse(
            invoice_dict['res_id'])
        self.assertEqual(invoice.is_capital_fundraising, 1)
        self.assertEqual(invoice.fundraising_category_id.id, self.category_id)
        self.assertEqual(invoice.invoice_line_ids[0].quantity, self.share_qty)
        self.assertEqual(invoice.state, 'open')
