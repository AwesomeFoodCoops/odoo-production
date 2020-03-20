from odoo.tests import common


class AccountInvoiceRefundOptionTest(common.TransactionCase):
    """ Base class - Test the Account Invoice Refund Option.
    """

    def setUp(self):
        super(AccountInvoiceRefundOptionTest, self).setUp()
        # Useful models
        self.account_invoice_obj = self.env['account.invoice']
        self.account_invoice_refund_obj = self.env['account.invoice.refund']

        self.payment_term = self.env.ref('account.account_payment_term_advance')
        self.journalrec = self.env['account.journal'].search([
            ('type', '=', 'sale')], limit=1)
        self.partner3 = self.env.ref('base.res_partner_3')
        incom_account = self.env.ref('account.data_account_type_revenue')
        account_id = self.env['account.account'].search([
            ('user_type_id', '=', incom_account.id)], limit=1).id

        self.invoice_line_data = [
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
