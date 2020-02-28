from odoo.tests import common


class CoopCustomAccountTest(common.TransactionCase):
    """ Base class - Test the Coop Custom Account in invoice.
    """

    def setUp(self):
        super(CoopCustomAccountTest, self).setUp()
        # Useful models
        self.AccountInvoice = self.env['account.invoice']
        self.Account = self.env['account.account']
        self.UserType = self.env.ref('account.data_account_type_revenue')
        self.Account_id = self.Account.search([
            ('user_type_id', '=', self.UserType.id)], limit=1)
        self.Partner3 = self.env.ref('base.res_partner_3')
        self.Journalrec = self.env['account.journal'].search([
            ('type', '=', 'sale')])[0]
        self.Product5 = self.env.ref('product.product_product_5')
