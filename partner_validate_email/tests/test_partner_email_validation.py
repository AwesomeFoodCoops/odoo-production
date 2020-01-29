from .common import PartnerValidationTest


class TestPartnerValidation(PartnerValidationTest):

    def test_partner_email_validation(self):
        """ Test partner email validation """

        test_std_reg1 = self.ResPartner.create({
            'name': 'Test Partner 1',
            'email': 'xyz@example.com',
        })

        valid = test_std_reg1.validate_email_address(test_std_reg1.email)

        assert valid, "Wrong Email."

        test_std_reg2 = self.ResPartner.create({
            'name': 'Test Partner 1',
            'email': 'xyz@2saswaax.com',
        })

        valid2 = test_std_reg2.validate_email_address(test_std_reg2.email)
        assert valid2, "Partner has not been created, because of wrong email."
