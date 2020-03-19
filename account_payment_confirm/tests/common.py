from odoo.tests import common


class ImprovePaymentConfirmationTest(common.TransactionCase):
    """ Base class - Test the payment confirmation improvement.
    """

    def setUp(self):
        super(ImprovePaymentConfirmationTest, self).setUp()
        # Useful models
        self.account_invoice_obj = self.env['account.invoice']
        self.payment_model = self.env['account.payment']
        self.register_payments_obj = self.env['account.register.payments']
        self.register_payments_model = self.register_payments_obj.with_context(
            active_model='account.invoice')

        payment_term = self.env.ref('account.account_payment_term_advance')
        journalrec = self.env['account.journal'].search([
            ('type', '=', 'sale')])[0]
        self.bank_journal_euro = self.env['account.journal'].create({
            'name': 'Bank', 'type': 'bank', 'code': 'BNK67'})
        partner3 = self.env.ref('base.res_partner_3')
        incom_account = self.env.ref('account.data_account_type_revenue')
        account_id = self.env['account.account'].search([
            ('user_type_id', '=', incom_account.id)], limit=1).id
        self.payment = self.env.ref("account.account_payment_method_manual_in")

        invoice_line_data = [
            (0, 0,
                {
                    'product_id': self.env.ref('product.product_product_1').id,
                    'quantity': 40.0,
                    'account_id': account_id,
                    'name': 'product test 1',
                    'discount': 10.00,
                    'price_unit': 2.27,
                }
             ),
            (0, 0,
                {
                    'product_id': self.env.ref('product.product_product_2').id,
                    'quantity': 21.0,
                    'account_id': account_id,
                    'name': 'product test 2',
                    'discount': 10.00,
                    'price_unit': 2.77,
                }
             ),
        ]

        # Create an invoice
        self.Invoice = self.env['account.invoice'].create(dict(
            name="Test Customer Invoice",
            payment_term_id=payment_term.id,
            journal_id=journalrec.id,
            partner_id=partner3.id,
            invoice_line_ids=invoice_line_data
        ))

        # Validate an invoice
        self.Invoice.action_invoice_open()
