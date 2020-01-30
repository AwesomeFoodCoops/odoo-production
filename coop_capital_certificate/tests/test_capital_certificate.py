from .common import CapitalCertificateTest
from odoo import fields


class TestCapitalCertificate(CapitalCertificateTest):
    def test_capital_certificate01(self):
        """
            Test the Capital Certificate report can generate from the wizard
            and the Partner Selection should be 'All Partners'.
        """
        wiz = self.CapitalFund.create({
            'date_invoice': fields.Date.today(),
            'partner_id': self.Customer1.id,
            'category_id': self.category_id,
            'share_qty': self.share_qty,
            'payment_journal_id': self.payment_journal_id,
            'confirm_payment': True,
            'payment_term_id': self.payment_term_id
        })
        wiz.button_confirm()

        self.CCW_vals1 = {
            'year': fields.Date.today().year,
            'send_mail': False,
            'partner_selection': 'all'
        }
        CC_wizard = self.CapitalCertificateWizard.create(self.CCW_vals1)
        CC_wizard.generate_certificates(data={})

        CapitalCertificate = self.CapitalCertificate.search([
            ('partner_id', '=', self.Customer1.id)])

        self.assertEqual(len(CapitalCertificate.ids), 1)

    def test_capital_certificate02(self):
        """
            Test the Capital Certificate report can generate from the wizard
            and the Partner Selection should be 'List of Partners'.
        """
        wiz = self.CapitalFund.create({
            'date_invoice': fields.Date.today(),
            'partner_id': self.Customer2.id,
            'category_id': self.category_id,
            'share_qty': self.share_qty,
            'payment_journal_id': self.payment_journal_id,
            'confirm_payment': True,
            'payment_term_id': self.payment_term_id
        })
        wiz.button_confirm()

        self.CCW_vals2 = {
            'year': fields.Date.today().year,
            'send_mail': False,
            'partner_selection': 'list',
            'partner_ids': [(6, 0, [self.Customer2.id])]
        }
        CC_wizard = self.CapitalCertificateWizard.create(self.CCW_vals2)
        CC_wizard.generate_certificates(data={})

        CapitalCertificate = self.CapitalCertificate.search([
            ('partner_id', '=', self.Customer2.id)])
        self.assertEqual(len(CapitalCertificate.ids), 1)
