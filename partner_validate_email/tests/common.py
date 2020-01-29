from odoo.tests import common


class PartnerValidationTest(common.TransactionCase):
    """ Base class - Test Partner Email.
    """
    def setUp(self):
        super(PartnerValidationTest, self).setUp()

        self.ResPartner = self.env['res.partner']
