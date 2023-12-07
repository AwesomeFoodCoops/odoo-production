# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today Druidoo (<info@druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    can_reconcile_expense = fields.Boolean(
        help='Technical field',
        compute='_compute_can_reconcile_expense')

    can_reconcile_pos = fields.Boolean(
        help='Technical field',
        compute='_compute_can_reconcile_pos')

    @api.multi
    def _compute_can_reconcile_expense(self):
        for rec in self:
            rec.can_reconcile_expense = \
                bool(rec.journal_id.bank_expense_account_id)

    @api.multi
    def _compute_can_reconcile_pos(self):
        for rec in self:
            rec.can_reconcile_pos = bool(rec.journal_id.cb_child_ids)

    @api.multi
    def button_reconcile_bank_expense(self):
        """ Tries to automatically reconcile bank expenses """
        self.ensure_one()
        count = self.line_ids._reconcile_bank_expense()
        if count == 0:
            raise UserError(_(
                'No line is matched to Bank Expense Pattern'
            ))

    @api.multi
    def button_reconcile_pos(self):
        self.ensure_one()
        self._reconcile_pos()

    @api.multi
    def _reconcile_pos(self):
        """
        It will try to match the account moves of every CB journal
        with a single statement line in our bank account.

        If contactless matching is enabled, it will also try 2-lines
        combinations.

        If there's a match, it will create the corresponding account.moves
        and reconcile everything.
        """
        for rec in self:

            if not rec.journal_id.cb_child_ids:
                raise UserError(_(
                    'The journal %s has no CB Child Journals.'
                    ) % rec.journal_id.display_name)

            if not rec.journal_id.cb_lines_domain:
                raise UserError(_(
                    'The journal %s has no CB Lines Domain.'
                    ) % rec.journal_id.display_name)

            if (
                rec.journal_id.cb_contactless_matching
                and not rec.journal_id.cb_contactless_lines_domain
            ):
                raise UserError(_(
                    'The journal %s has no CB Contactless Lines Domain.'
                    ) % rec.journal_id.display_name)

            # Lines that match the standard pattern
            domain = [
                ('statement_id', '=', rec.id),
                ('journal_entry_ids', '=', False),
            ]
            domain += safe_eval(rec.journal_id.cb_lines_domain)
            lines = rec.line_ids.search(domain)
            # Process regular 1-line matching first
            not_reconciled_lines = rec._pos_reconcile_lines(lines)

            # Manage contact-less matching
            if rec.journal_id.cb_contactless_matching:
                domain = [
                    ('statement_id', '=', rec.id),
                    ('journal_entry_ids', '=', False),
                ]
                domain += safe_eval(rec.journal_id.cb_contactless_lines_domain)
                alt_lines = rec.line_ids.search(domain)
                # Process alt lines 1-line matching first
                not_reconciled_alt_lines = rec._pos_reconcile_lines(alt_lines)

                # Process combinations
                if not_reconciled_lines and not_reconciled_alt_lines:
                    rec._pos_reconcile_lines_combined(not_reconciled_lines, not_reconciled_alt_lines)

    def _pos_reconcile_lines(self, lines):
        '''
        This will try to find the statement for each line,
        and reconcile it with it.

        Returns not_reconciled_lines
        '''
        self.ensure_one()
        reconciled_lines = self.env['account.bank.statement.line']
        for line in lines:
            statement = self._find_pos_statement(
                date=line.date, amount=line.amount)
            # Ignore not matching
            if not statement:
                continue
            elif len(statement) > 1:
                _logger.debug(
                    'Multiple possible statements for "%s" line. '
                    'Ignoring..' % (line.name))
                continue
            # Reconcile lines
            self._pos_reconcile_statement_with_lines(
                lines=line, statement=statement)
            reconciled_lines |= line
        return (lines - reconciled_lines)

    def _pos_reconcile_lines_combined(self, lines, alt_lines):
        '''
        This will try to find the statatement using a combination
        of lines (1+1 matching)

        Returns a tuple with:
            (not_reconciled_lines, not_reconciled_alt_lines)
        '''
        self.ensure_one()
        delta_days = self.journal_id.cb_contactless_delta_days
        reconciled_lines = self.env['account.bank.statement.line']
        reconciled_alt_lines = self.env['account.bank.statement.line']
        for line in lines:
            for alt_line in alt_lines:
                # if line is already reconciled, skip it
                if alt_line in reconciled_alt_lines:
                    continue
                # Ignore lines that do not comply cb_contactless_delta_days
                date_limit_min = (line.date - timedelta(days=delta_days))
                date_limit_max = (line.date + timedelta(days=delta_days))
                if (
                    alt_line.date > date_limit_max
                    or alt_line.date < date_limit_min
                ):
                    continue
                # Try to find statement
                statement = self._find_pos_statement(
                    date=line.date, amount=(line.amount + alt_line.amount))
                # Ignore not matching
                if not statement:
                    continue
                elif len(statement) > 1:
                    _logger.debug(
                        'Multiple possible statements for "%s" and "%s" line. '
                        'Ignoring..' % (line.name, alt_line.name))
                    continue
                # Reconcile lines
                self._pos_reconcile_statement_with_lines(
                    lines=(line | alt_line), statement=statement)
                reconciled_lines |= line
                reconciled_alt_lines |= alt_line
                break  # line has already reconciled, break the loop then.
        # Return tuple
        return (
            lines - reconciled_lines,
            alt_lines - reconciled_alt_lines,
        )

    def _find_pos_statement(self, date, amount):
        '''
        Finds a pos statement by amount, using
        the setup on the journal
        '''
        self.ensure_one()
        rounding = self.journal_id.cb_rounding
        # Delta days is used only to get past statement, but not future ones
        max_date = date
        min_date = date - timedelta(days=self.journal_id.cb_delta_days)
        # Find matching statements
        pos_statement_ids = self.env['account.bank.statement'].search([
            ('journal_id', 'in', self.journal_id.cb_child_ids.ids),
            ('date', '<=', max_date),
            ('date', '>=', min_date),
            ('balance_end_real', '>=', round(amount - rounding, 2)),
            ('balance_end_real', '<=', round(amount + rounding, 2)),
            ('line_ids', '!=', False),
        ])
        _logger.debug(
            'Searching POS Statements ('
            'min_date=%s, max_date=%s, amount=%s, rounding=%s, child_ids=%s'
            '): %s' % (
                min_date, max_date, amount, rounding,
                self.journal_id.cb_child_ids,
                pos_statement_ids))
        # Filter statements that are already reconciled
        ignored_pos_statement_ids = self.env['account.bank.statement']
        debit_account_id = self.journal_id.default_debit_account_id.id
        for st in pos_statement_ids:
            reconciled_move_lines = st.move_line_ids.filtered(
                lambda l: (
                    l.reconciled and l.account_id.id == debit_account_id))
            if reconciled_move_lines:
                _logger.debug(
                    'There are debits on the journal and they are reconciled.')
                ignored_pos_statement_ids |= st
        pos_statement_ids -= ignored_pos_statement_ids
        # Return found statements
        return pos_statement_ids

    def _pos_reconcile_statement_with_lines(self, lines, statement):
        self.ensure_one()
        st_debit_account_id = \
            statement.journal_id.default_debit_account_id.id
        st_credit_account_id = \
            statement.journal_id.default_credit_account_id.id
        lines_to_reconcile = []
        for line in lines:
            move_line_vals = {
                'name': '%s %s %s' % (
                    statement.journal_id.name,
                    statement.date,
                    statement.name),
                'debit': 0.0,
                'credit': abs(line.amount),
                'journal_id': self.journal_id.id,
                'date': statement.date,
                'account_id': st_credit_account_id,
            }

            _logger.info('Creating reconciliation line: %s' % move_line_vals)
            line.process_reconciliation([], [], [move_line_vals])
            # Now let's settle this line with the statement lines
            for move_line in statement.move_line_ids:
                if (
                        move_line.account_id.id == st_debit_account_id
                        and move_line.id not in lines_to_reconcile
                        and not move_line.reconciled
                ):
                    lines_to_reconcile.append(move_line.id)
            for move_line in line.journal_entry_ids:
                if (
                        move_line.account_id.id == st_credit_account_id
                        and move_line.id not in lines_to_reconcile
                ):
                    lines_to_reconcile.append(move_line.id)
        # Process reconciliation
        move_lines = self.env['account.move.line'].browse(lines_to_reconcile)
        move_lines.reconcile()
