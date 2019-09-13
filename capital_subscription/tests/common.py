from odoo.tests import common
from odoo import fields


class CapitalSubscriptionTest(common.TransactionCase):
    """ Base class - Test the Capital Subscription.
    """

    def setUp(self):
        super(CapitalSubscriptionTest, self).setUp()
        ModelData = self.env['ir.model.data']
        self.CapitalFund = self.env['capital.fundraising.wizard']

        self.date_invoice = fields.Date.today()

        self.partner_agrolite_id = ModelData.xmlid_to_res_id('base.res_partner_2')
        self.category_id = ModelData.xmlid_to_res_id('capital_subscription.capital_fundraising_category_A')
        self.share_qty = 10
        self.payment_journal_id = ModelData.xmlid_to_res_id('capital_subscription.capital_journal')
        self.payment_term_id = ModelData.xmlid_to_res_id('account.account_payment_term_immediate')
