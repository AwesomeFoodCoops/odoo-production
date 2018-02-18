# -*- coding: utf-8 -*-

from openerp import api, models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    reconciled_account = fields.Boolean(
        compute='_compute_field_reconciled_account',
        string='Bank Reconciliation',
        store=True
    )
    journal_credit_ids = fields.One2many(
        'account.journal',
        'default_credit_account_id',
        string='Account Journal Credit'
    )
    journal_debit_ids = fields.One2many(
        'account.journal',
        'default_debit_account_id',
        string='Account Journal Debit'
    )

    @api.multi
    @api.depends('journal_credit_ids', 'journal_debit_ids')
    def _compute_field_reconciled_account(self):
        for account in self:
            account_journal = account.journal_credit_ids |\
                account.journal_debit_ids
            if account_journal:
                if any(journal.type == 'bank' for journal in account_journal):
                    account.reconciled_account = True
                else:
                    account.reconciled_account = False
            else:
                account.reconciled_account = False
