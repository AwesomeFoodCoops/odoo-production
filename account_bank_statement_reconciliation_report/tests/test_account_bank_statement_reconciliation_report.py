from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase
from odoo import fields


class TestReconciliationReport(TransactionCase):
    """
        Tests for Account Invoice Merge.
    """
    def setUp(self):
        super().setUp()
        self.journal = self.env['account.journal'].create({
            'name': 'Test Bank Journal',
            'code': 'TBJ1',
            'type': 'bank',
        })
        exp_acc = self.env['account.account'].search([
            ('user_type_id.name', '=', 'Expenses')], limit=1)
        self.bank_statement = self.env['account.bank.statement'].create(
            {
                'journal_id': self.journal.id,
                'account_id': self.journal.default_credit_account_id.id,
                'date': fields.Date.today(),
                'accounting_date': fields.Date.today() + relativedelta(days=1),
                'line_ids': [(0, 0, {'name': 'Test Line',
                                     'date': fields.Date.today(),
                                     'account_id': exp_acc.id,
                                     'amount': 200.00,
                                     }
                              ),
                             ]
            }
        )
        self.statement_line_1 = self.bank_statement.line_ids[0]
        self.statement_line_1.fast_counterpart_creation()
        self.wiz_rec = self.env['bank.reconciliation.summary.wizard'].create({
            'journal_id': self.journal.id,
            'analysis_date': fields.Date.today(),
        })

    def test_001_reconciliation_summary_report(self):
        reconciliation_summary = self.env[
            'report.bank_reconciliation_summary_xlsx']

        move_lines, bank_statement_lines, bank_balance, account_balance = \
            reconciliation_summary.get_data(self.wiz_rec)
        self.assertEqual(bank_statement_lines[0], self.statement_line_1,
                         'Bank Statement line is not created properly!')
        self.assertEqual(bank_balance, 200.0,
                         'Bank Balance has to be 200.00')
        self.assertEqual(account_balance, 0.0,
                         'Account Balance has to be 0.00')

    def test_002_reconciliation_summary_report(self):
        reconciliation_summary = self.env[
            'report.bank_reconciliation_summary_xlsx']
        self.wiz_rec.analysis_date += relativedelta(days=1)

        move_lines, bank_statement_lines, bank_balance, account_balance = \
            reconciliation_summary.get_data(self.wiz_rec)
        self.assertFalse(bank_statement_lines,
                         'Bank Statement line is not created properly!')
        self.assertEqual(bank_balance, 200.0,
                         'Bank Balance has to be 200.00')
        self.assertEqual(account_balance, -200.0,
                         'Account Balance has to be -200.0')
