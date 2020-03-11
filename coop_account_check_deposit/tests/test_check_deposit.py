
from openerp.addons.account_check_deposit.tests.test_check_deposit\
    import TestPayment
import time


class TestDepositPayment(TestPayment):

    def setUp(self):
        super(TestDepositPayment, self).setUp()

        self.destination_journal = self.journal_model.search(
            [('code', '=', 'BILL')], limit=1)
        self.destination_journal.default_debit_account_id\
            = self.bank_account_id
        self.destination_journal.default_credit_account_id\
            = self.bank_account_id

    def create_check_deposit(self, move_lines):
        """ Returns an validated check deposit """
        check_deposit = self.check_deposit_model.create({
            'journal_id': self.bank_journal.id,
            'bank_journal_id': self.bank_journal.id,
            'deposit_date': time.strftime('%Y-%m-%d'),
            'currency_id': self.currency_eur_id,
            'destination_journal_id': self.destination_journal.id,
        })
        for move_line in move_lines:
            move_line.check_deposit_id = check_deposit
        check_deposit.validate_deposit()
        return check_deposit
