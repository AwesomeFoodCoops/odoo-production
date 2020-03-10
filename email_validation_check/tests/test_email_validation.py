from odoo.tests import common


class TestEmailValidation(common.TransactionCase):

    def test_email_validation01(self):
        """ Test email validation """
        self.ResPartner = self.env['res.partner']

        partner = self.env.ref(
            'coop_shift.standard_member_1')

        partner.check_email_validation_string('test@example.com')
        self.assertEqual(
            partner.is_checked_email,
            True, 'Invalid email')
