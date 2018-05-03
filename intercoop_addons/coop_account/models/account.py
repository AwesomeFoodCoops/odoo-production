# -*- coding: utf-8 -*-

from openerp import api, models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    reconciled_account = fields.Boolean(
        compute='_compute_field_reconciled_account',
        string='Bank Reconciliation',
        store=True,
        help="If true, account moves will be able to have at most only one " +
        "account move line linked to this account (or to another account " +
        "with 'Bank reconciliation' is true)"
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
    # field for checking to reconciled and create new move by manual
    reconcile_liquidity_type = fields.Boolean(
        string="Reconciliation for Cash & Bank account type",
        help="If true, account move will be create when reconcile manual" +\
            " even type of this account is cash and bank")

    @api.multi
    @api.depends('journal_credit_ids', 'journal_debit_ids',
                 'journal_credit_ids.type', 'journal_debit_ids.type')
    def _compute_field_reconciled_account(self):
        for account in self:
            account_journal = account.journal_credit_ids |\
                account.journal_debit_ids
            if account_journal.filtered(lambda j: j.bank_account_id):
                if any(journal.type == 'bank' for journal in account_journal):
                    account.reconciled_account = True
                else:
                    account.reconciled_account = False
            else:
                account.reconciled_account = False
