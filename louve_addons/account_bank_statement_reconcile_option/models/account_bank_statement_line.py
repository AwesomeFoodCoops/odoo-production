# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models
from openerp.tools import float_round
from openerp.osv import expression


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    # Overload Section
    def get_move_lines_for_reconciliation(
            self, excluded_ids=None, str=False, offset=0, limit=None,
            additional_domain=None, overlook_partner=False):
        if self.journal_id.reconcile_mode == 'journal_account':
            domain = self._get_domain_reconciliation(
                excluded_ids, str, overlook_partner, additional_domain)
            return self.env['account.move.line'].search(
                domain, offset=offset, limit=limit,
                order="date_maturity asc, id asc")
        return super(
            AccountBankStatementLine, self).get_move_lines_for_reconciliation(
                excluded_ids=excluded_ids, str=str, offset=offset, limit=limit,
                additional_domain=additional_domain,
                overlook_partner=overlook_partner)

    def get_reconciliation_proposition(self, excluded_ids=None):
        """
        Modify the function to:
            - Load correct reconciliation proposition for Journal with Account
            Type = Account Journal
        """
        self.ensure_one()

        if self.journal_id.reconcile_mode == 'journal_account':
            if not excluded_ids:
                excluded_ids = []
            amount = self.amount_currency or self.amount
            company_currency = self.journal_id.company_id.currency_id
            st_line_currency = self.currency_id or self.journal_id.currency_id
            currency = (st_line_currency and st_line_currency !=
                        company_currency) and st_line_currency.id or False
            precision = st_line_currency and st_line_currency.decimal_places \
                or company_currency.decimal_places
            params = {'company_id': self.env.user.company_id.id,
                      'account_payable_receivable':
                      (self.journal_id.default_credit_account_id.id,
                       self.journal_id.default_debit_account_id.id),
                      'amount':
                      float_round(amount, precision_digits=precision),
                      'partner_id': self.partner_id.id,
                      'excluded_ids': tuple(excluded_ids),
                      'ref': self.name,
                      }
            # Look for structured communication match
            if self.name:
                add_to_select = \
                    ", CASE WHEN aml.ref = %(ref)s " + \
                    "THEN 1 ELSE 2 END as temp_field_order "
                add_to_from = " JOIN account_move m ON m.id = aml.move_id "

                select_clause, from_clause, where_clause = \
                    self._get_common_sql_query(overlook_partner=True,
                                               excluded_ids=excluded_ids,
                                               split=True)
                sql_query = select_clause + add_to_select + \
                    from_clause + add_to_from + where_clause
                sql_query += " AND (aml.ref= %(ref)s or m.name = %(ref)s) \
                        AND aml.account_id IN %(account_payable_receivable)s \
                        AND aml.statement_id IS NULL \
                        ORDER BY temp_field_order, date_maturity asc, \
                        aml.id asc"
                self.env.cr.execute(sql_query, params)
                results = self.env.cr.fetchone()
                if results:
                    return self.env['account.move.line'].browse(results[0])

            # Look for a single move line with the same amount
            field = currency and 'amount_residual_currency' \
                or 'amount_residual'
            liquidity_field = currency and 'amount_currency' or amount > 0 \
                and 'debit' or 'credit'
            liquidity_amt_clause = currency and '%(amount)s' or \
                'abs(%(amount)s)'
            sql_query = \
                self._get_common_sql_query(excluded_ids=excluded_ids) + \
                "AND aml.account_id IN %(account_payable_receivable)s" \
                " AND aml.statement_id IS NULL" \
                " AND (" + field + " = %(amount)s OR " + \
                "(acc.internal_type = 'liquidity' AND " + \
                liquidity_field + " = " + liquidity_amt_clause + ")) \
                    ORDER BY date_maturity asc, aml.id asc LIMIT 1"
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.fetchone()
            if results:
                return self.env['account.move.line'].browse(results[0])
            return self.env['account.move.line']

        else:
            return super(AccountBankStatementLine, self).\
                get_reconciliation_proposition(excluded_ids=excluded_ids)

    def _get_domain_reconciliation(
            self, excluded_ids, str, overlook_partner, additional_domain):
        reconciliation_aml_accounts = [
            self.journal_id.default_credit_account_id.id,
            self.journal_id.default_debit_account_id.id,
        ]
        bank_reconcile_account_allowed_ids =\
            self.journal_id.bank_reconcile_account_allowed_ids.ids or []
        reconciliation_account_all = reconciliation_aml_accounts + \
            bank_reconcile_account_allowed_ids

        domain = [
            '&', '&', ('statement_id', '=', False),
            ('reconciled', '=', False),
            ('account_id', 'in', reconciliation_account_all)]

        if self.partner_id.id and not overlook_partner:
            domain = expression.AND(
                [domain, [('partner_id', '=', self.partner_id.id)]])

        # Domain factorized for all reconciliation use cases
        ctx = dict(self._context or {})
        ctx['bank_statement_line'] = self
        generic_domain = self.env['account.move.line'].with_context(
            ctx).domain_move_lines_for_reconciliation(
            excluded_ids=excluded_ids, str=str)
        domain = expression.AND([domain, generic_domain])

        # Domain from caller
        if additional_domain is None:
            additional_domain = []
        else:
            additional_domain = expression.normalize_domain(additional_domain)
        domain = expression.AND([domain, additional_domain])

        return domain
