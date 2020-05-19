# -*- coding: utf-8 -*-
##############################################################################
#
#    POS Payment Terminal module for Odoo
#    Copyright (C) 2017 Iván Todorovich <ivan.todorovich@druidoo.io>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from datetime import datetime, timedelta

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
            rec.can_reconcile_pos = \
                bool(rec.journal_id.cb_child_ids)

    @api.multi
    def button_reconcile_bank_expense(self):
        """ Tries to automatically reconcile bank expenses """
        self.ensure_one()
        self.line_ids._reconcile_bank_expense()

    @api.multi
    def button_reconcile_pos(self):
        self.ensure_one()
        self._reconcile_pos()

    @api.multi
    def _reconcile_pos(self):
        """
        It will try to match the account moves of every CB journal
        with a single statement line in our bank account.
        If there's a match, it will create the corresponding account.moves
        and reconcile everything.
        """
        for rec in self:

            if not rec.journal_id.cb_child_ids:
                raise UserError(_(
                    'The journal %s has no CB journals.'
                    ) % rec.journal_id.display_name)

            if not rec.journal_id.cb_contract_number:
                raise UserError(_(
                    'The journal %s has no CB Contract number.'
                    ) % rec.journal_id.display_name)

            if rec.journal_id.cb_contactless_matching and not rec.journal_id.cb_contract_number_contactless:
                raise UserError(_(
                    'The journal %s has no CT Contract number.'
                ) % rec.journal_id.display_name)
            # Process lines that match the pattern
            cb_line_ids = rec.line_ids.search([
                ('statement_id', '=', rec.id),
                ('journal_entry_ids', '=', False),
                ('name', 'ilike', '%%%s%%' % rec.journal_id.cb_contract_number),
            ])
            # Process CB Statement lines first
            not_reconcile_cb_lines = rec._get_correct_cb_statement_id(cb_line_ids)
            # Process CT Statement lines first
            not_reconcile_ct_lines = self.env['account.bank.statement.line']
            if rec.journal_id.cb_contactless_matching:
                ct_line_ids = rec.line_ids.search([
                    ('statement_id', '=', rec.id),
                    ('journal_entry_ids', '=', False),
                    ('name', 'ilike', '%%%s%%' % rec.journal_id.cb_contract_number_contactless),
                ])
                not_reconcile_ct_lines = rec._get_correct_ct_statement_id(ct_line_ids)
            # Process CB+CT Statement lines
            if not_reconcile_cb_lines and not_reconcile_ct_lines:
                rec._get_correct_cb_ct_statement_id(not_reconcile_cb_lines, not_reconcile_ct_lines)

    def _get_correct_cb_statement_id(self, cb_line_ids):
        not_reconcile_lines = self.env['account.bank.statement.line']
        for line in cb_line_ids:
            delta_days = self.journal_id.cb_delta_days
            rounding = self.journal_id.cb_rounding
            res = self.get_correct_pos_statement(line.date, line.amount,delta_days,rounding)
            if not res or len(res) > 1:
                _logger.debug('Unable to match line or multiple possible statements for "%s" line' % line.name)
                not_reconcile_lines |= line
                continue
            self.process_statement_reconcile(line, res)
        return not_reconcile_lines

    def _get_correct_ct_statement_id(self, ct_line_ids):
        not_reconcile_lines = self.env['account.bank.statement.line']
        if ct_line_ids:
            for line in ct_line_ids:
                delta_days = self.journal_id.cb_contactless_delta_days
                rounding = self.journal_id.cb_rounding
                res = self.get_correct_pos_statement(line.date, line.amount, delta_days, rounding)
                if not res or len(res) > 1:
                    _logger.debug('Unable to match line or multiple possible statements for "%s" line' % line.name)
                    not_reconcile_lines |= line
                    continue
                self.process_statement_reconcile(line, res)
        return not_reconcile_lines

    def _get_correct_cb_ct_statement_id(self, not_reconcile_cb_lines, not_reconcile_ct_lines):
        for cb_line in not_reconcile_cb_lines:
            for ct_line in not_reconcile_ct_lines:
                total_amount = cb_line.amount + ct_line.amount
                delta_days = self.journal_id.cb_delta_days
                ct_delta_days = self.journal_id.cb_contactless_delta_days
                rounding = self.journal_id.cb_rounding
                res = self.get_correct_pos_statement(cb_line.date, total_amount, delta_days, rounding, ct_date=ct_line.date, ct_delta_days=ct_delta_days)
                if not res or len(res) > 1:
                    _logger.debug('Unable to match line or multiple possible statements for "%s" and "%s" line' % (cb_line.name, ct_line.name))
                    continue
                self.process_statement_reconcile(cb_line,res, ct_line=ct_line)

    def get_correct_pos_statement(self, line_date, amount, delta_days, rounding, ct_date=False,ct_delta_days=0):
        limit_date = (
                datetime.strptime(line_date, '%Y-%m-%d')
                - timedelta(days=delta_days))
        pos_statement_ids = self.env['account.bank.statement'].search([
            ('date', '<=', line_date),
            ('date', '>=', limit_date.strftime('%Y-%m-%d')),
            ('balance_end_real', '>=', round(amount - rounding, 2)),
            ('balance_end_real', '<=', round(amount + rounding, 2)),
            ('line_ids', '!=', False),
        ])
        if not pos_statement_ids and ct_date:
            ct_limit_date = (
                    datetime.strptime(ct_date, '%Y-%m-%d')
                    - timedelta(days=ct_delta_days))
            pos_statement_ids = self.env['account.bank.statement'].search([
                ('date', '<=', ct_date),
                ('date', '>=', ct_limit_date.strftime('%Y-%m-%d')),
                ('balance_end_real', '>', round(amount - rounding, 2)),
                ('balance_end_real', '<', round(amount + rounding, 2)),
                ('line_ids', '!=', False),
            ])

        _logger.debug('Possible CB/CT/CB+CT statements: %d' % len(pos_statement_ids))
        ignore_cb_statement_ids = []
        for pos_statement_id in pos_statement_ids:
            for l in pos_statement_id.move_line_ids:
                reconciled_move_lines_count = \
                    len(pos_statement_id.move_line_ids.filtered(lambda l: l.reconciled and l.account_id.id == \
                                                                          self.journal_id.default_debit_account_id.id))
                if reconciled_move_lines_count:
                    if len(pos_statement_id) != reconciled_move_lines_count:
                        _logger.debug('Level 2: POS partially processed by the bank.')
                    else:
                        _logger.debug('Case 1: There are debits on the journal and they are reconciled.')
                    # In any case, don't use this statement
                    ignore_cb_statement_ids.append(pos_statement_id.id)
        pos_statement_ids = pos_statement_ids.filtered(lambda s: s.id not in ignore_cb_statement_ids)
        return pos_statement_ids

    def process_statement_reconcile(self, lines, statement_id, ct_line=False):
        if ct_line:
            lines |= ct_line
        lines_to_reconcile = []
        for line in lines:
            move_line_vals = {
                'name': '%s %s %s %s' % (
                    self.journal_id.cb_contract_number,
                    statement_id.journal_id.name,
                    statement_id.date,
                    statement_id.name),
                'debit': 0.0,
                'credit': abs(line.amount),
                'journal_id': self.journal_id.id,
                'date': statement_id.date,
                'account_id': statement_id.journal_id.default_credit_account_id.id,
            }

            _logger.debug('Creating reconciliation line: %s' % move_line_vals)
            line.process_reconciliation([], [], [move_line_vals])
            # Now let's settle this line with the statement lines
            for move_line in statement_id.move_line_ids:
                if (
                        move_line.account_id.id == statement_id.journal_id.default_debit_account_id.id
                        and move_line.id not in lines_to_reconcile
                ):
                    lines_to_reconcile.append(move_line.id)

            for move_line in line.journal_entry_ids.mapped('line_ids'):
                if (
                        move_line.account_id.id == statement_id.journal_id.default_credit_account_id.id
                        and move_line.id not in lines_to_reconcile
                ):
                    lines_to_reconcile.append(move_line.id)
        self.env['account.move.line.reconcile'].with_context(active_ids=lines_to_reconcile).create(
            {}).trans_rec_reconcile_full()
