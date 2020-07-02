from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestBankStatementReconciliation(AccountingTestCase):

    def setUp(self):
        super(TestBankStatementReconciliation, self).setUp()
        self.bs_model = self.env['account.bank.statement']
        self.bsl_model = self.env['account.bank.statement.line']
        self.acc_model = self.env['account.account']
        self.partner = self.env['res.partner'].create({'name': 'test'})

    def test_reconciliation_reconcile_bank_expense(self):
        st_line = self.create_statement_line(100)
        st_line.statement_id.button_reconcile_bank_expense()
        move_id = st_line.statement_id.mapped('move_line_ids')\
            .mapped('move_id')
        self.assertEqual(
            move_id.state,
            'posted',
            '''The Journal Entry of this bank statement
            state should now "posted"''')

    def create_statement_line(self, st_line_amount):
        bank_expense_account_id = self.acc_model.search([
            ('user_type_id', '=', 'Expenses'), ('name', '=', 'Bank Fees')])
        if bank_expense_account_id:
            journal = self.bs_model.with_context(journal_type='bank')\
                ._default_journal()
            journal.bank_expense_name_pattern = 'expense_name'
            journal.bank_expense_ref_pattern = 'expense_ref'
            journal.bank_expense_note_pattern = 'expense_note'
            journal.bank_expense_account_id = bank_expense_account_id[0].id
            bank_stmt = self.bs_model.create({
                'journal_id': journal.id,
                'can_reconcile_expense': True,
            })

            bank_stmt_line = self.bsl_model.create({
                'name': 'expense_name',
                'ref': 'expense_ref',
                'note': 'expense_note',
                'statement_id': bank_stmt.id,
                'partner_id': self.partner.id,
                'amount': st_line_amount,
                })

            return bank_stmt_line

    def test_reconciliation_reconcile_pos(self):
        st_line = self.create_pos_statement_line(100)
        st_line.statement_id.button_reconcile_pos()
        move_id = st_line.statement_id.mapped('move_line_ids')\
            .mapped('move_id')
        self.assertEqual(
            move_id.state,
            'posted',
            '''The Journal Entry of this bank statement state
            should now "posted"''')

    def create_pos_statement_line(self, st_line_amount):
        journal = self.bs_model.with_context(journal_type='bank')\
            ._default_journal()
        journal.cb_child_ids = [(6, 0, [journal.id])]
        journal.cb_lines_domain = "[('name', 'ilike', '%CB/CONT/01%')]"

        bank_stmt = self.bs_model.create({
            'journal_id': journal.id,
            'can_reconcile_pos': True,
            'balance_end_real': st_line_amount
        })

        bank_stmt_line = self.bsl_model.create({
            'name': 'CB/CONT/01',
            'statement_id': bank_stmt.id,
            'partner_id': self.partner.id,
            'amount': st_line_amount,
            'journal_entry_ids': False
        })

        return bank_stmt_line
