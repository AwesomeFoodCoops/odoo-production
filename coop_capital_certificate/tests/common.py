from odoo.tests import common


class CapitalCertificateTest(common.TransactionCase):
    """ Base class - Test the Capital Certificate report.
    """

    def setUp(self):
        super(CapitalCertificateTest, self).setUp()

        # Useful models
        self.CapitalCertificate = self.env['capital.certificate']
        self.CapitalCertificateWizard = self.env['capital.certificate.wizard']
        self.CapitalFund = self.env['capital.fundraising.wizard']
        self.Customer1 = self.env.ref(
            'capital_subscription.middle_class_partner')
        self.Customer2 = self.env.ref('base.res_partner_2')

        self.CapitalAccount = self.env.ref(
            'capital_subscription.paid_capital_account_category_A')
        self.CapitalAccount.write({'reconcile': True})

        self.Product = self.env.ref(
            'capital_subscription.product_fundraising_category_A')
        self.Product.write({
            'property_account_income_id': self.CapitalAccount.id
        })

        self.category_id = self.env.ref(
            'capital_subscription.capital_fundraising_category_A').id
        self.share_qty = 10
        self.payment_journal_id = self.env.ref(
            'capital_subscription.capital_journal').id
        self.payment_journal = self.env.ref(
            'capital_subscription.capital_journal')
        self.payment_term_id = self.env.ref(
            'account.account_payment_term_immediate').id
        self.payment_journal.confirm_fundraising_payment = 'allways'
        self.env.ref('base.main_company').write({
            'capital_certificate_header': 'Capital Certificate Header'
        })
