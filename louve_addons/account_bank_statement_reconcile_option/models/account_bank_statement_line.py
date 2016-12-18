# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    # Overload Section
    def get_move_lines_for_reconciliation(
            self, excluded_ids=None, str=False, offset=0, limit=None,
            additional_domain=None, overlook_partner=False):
        if self.journal_id.reconcile_mode == 'journal_account':
            reconciliation_aml_accounts = [
                self.journal_id.default_credit_account_id.id,
                self.journal_id.default_debit_account_id.id,
            ]
            domain = [
                '&', ('statement_id', '=', False),
                ('account_id', 'in', reconciliation_aml_accounts)]
            return self.env['account.move.line'].search(
                domain, offset=offset, limit=limit,
                order="date_maturity asc, id asc")
        return super(
            AccountBankStatementLine, self).get_move_lines_for_reconciliation(
                excluded_ids=excluded_ids, str=str, offset=offset, limit=limit,
                additional_domain=additional_domain,
                overlook_partner=overlook_partner)
