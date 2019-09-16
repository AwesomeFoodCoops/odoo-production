from odoo.tests import common
from odoo import fields


class CoopMembershipTest(common.TransactionCase):
    """ Base class - Test the Coop Membership Test.
    """

    def setUp(self):
        super(CoopMembershipTest, self).setUp()

        ModelData = self.env['ir.model.data']

        self.date_invoice = fields.Date.today()

        self.ResPartner = self.env['res.partner']
        self.CapitalFundWizard = self.env['capital.fundraising.wizard']
        self.ShiftTemplateRegLine = \
            self.env['shift.template.registration.line']

        self.ShiftTemplateTicket = self.env['shift.template.ticket']

        self.standard_member_1 = ModelData.xmlid_to_res_id(
            'coop_shift.standard_member_1')
        self.capital_fundraising_category_A = ModelData.xmlid_to_res_id(
            'capital_subscription.capital_fundraising_category_A')
        self.payment_journal_id = ModelData.xmlid_to_res_id(
            'capital_subscription.capital_journal')
        self.payment_term_id = ModelData.xmlid_to_res_id(
            'account.account_payment_term_immediate')

        self.shift_template = ModelData.xmlid_to_res_id(
            'coop_shift.standard_template_1')
