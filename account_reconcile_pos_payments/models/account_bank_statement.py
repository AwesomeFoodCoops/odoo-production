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

            # Process lines that match the pattern
            line_ids = rec.line_ids.search([
                ('statement_id', '=', rec.id),
                ('journal_entry_ids', '=', False),
                ('name', 'ilike', '%%%s%%' % rec.journal_id.cb_contract_number),
            ])

            i = 0
            for line in line_ids:
                i += 1
                _logger.debug('Processing line %s (%d/%d)' % (line.name, i, len(line_ids)))

                # Try to find a CB statement older than our statement line
                # but not older than 3 days before
                limit_date = (
                    datetime.strptime(line.date, '%Y-%m-%d')
                    - timedelta(days=rec.journal_id.cb_delta_days))
                cb_statement_ids = self.env['account.bank.statement'].search([
                    ('date', '<=', line.date),
                    ('date', '>=', limit_date.strftime('%Y-%m-%d')),
                    ('balance_end_real', '>', round(line.amount-0.01, 2)),
                    ('balance_end_real', '<', round(line.amount+0.01, 2)),
                    ('line_ids', '!=', False),
                ])

                _logger.debug('Possible CB statements: %d' % len(cb_statement_ids))

                # Only accept statements whose account movements are fully unreconciled
                ignore_cb_statement_ids = []
                for cb_statement_id in cb_statement_ids:
                    reconciled_move_lines_count = \
                        len(cb_statement_id.move_line_ids.filtered(lambda l:
                            l.reconciled and l.account_id.id == \
                                rec.journal_id.default_debit_account_id.id))
                    if reconciled_move_lines_count:
                        if len(cb_statement_id) != reconciled_move_lines_count:
                            _logger.warning('Level 2: POS partially processed by the bank.')
                        else:
                            _logger.debug('Case 1: There are debits on the journal and they are reconciled.')
                        # In any case, don't use this statement
                        ignore_cb_statement_ids.append(cb_statement_id.id)
                cb_statement_ids = cb_statement_ids.filtered(lambda s: s.id not in ignore_cb_statement_ids)

                if not cb_statement_ids:
                    _logger.debug('Unable to match line "%s" to a CB statement' % line.name)
                    continue

                if len(cb_statement_ids)>1:
                    _logger.warning('There are multiple possible statements for this line. Unable to process. %s' % line)
                    continue

                # If we got this far, means we have a match!
                # Let's create the move line in our journal
                move_line_vals = {
                    'name': '%s %s %s %s' % (
                        rec.journal_id.cb_contract_number,
                        cb_statement_id.journal_id.name,
                        cb_statement_id.date,
                        cb_statement_id.name),
                    'debit': 0.0,
                    'credit': abs(line.amount),
                    'journal_id': rec.journal_id.id,
                    'date': cb_statement_id.date,
                    'account_id': cb_statement_id.journal_id.default_credit_account_id.id,
                }

                _logger.debug('Creating reconciliation line: %s' % move_line_vals)
                line.process_reconciliation([], [], [move_line_vals])

                # Now let's settle this line with the statement lines
                lines_to_reconcile = []

                for move_line in cb_statement_id.move_line_ids:
                    if (
                        move_line.account_id.id == cb_statement_id.journal_id.default_debit_account_id.id
                        and move_line.id not in lines_to_reconcile
                    ):
                        lines_to_reconcile.append(move_line.id)

                for move_line in line.journal_entry_ids.mapped('line_ids'):
                    if (
                        move_line.account_id.id == cb_statement_id.journal_id.default_credit_account_id.id
                        and move_line.id not in lines_to_reconcile
                    ):
                        lines_to_reconcile.append(move_line.id)

                # TODO: Also reconcile contactless lines here
                self.env['account.move.line.reconcile'].with_context(active_ids=lines_to_reconcile).create({}).trans_rec_reconcile_full()
