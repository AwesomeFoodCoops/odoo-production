# -*- coding: utf-8 -*-
##############################################################################
#
#    POS Payment Terminal module for Odoo
#    Copyright (C) 2014 Aurélien DUMAINE
#    Copyright (C) 2015 Akretion (www.akretion.com)
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
from openerp import models, fields, _, api
from openerp.exceptions import except_orm
import re
from datetime import datetime

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.multi
    def payment_terminal_bank_reconciliation(self):
        for bank_line in self:
            name = re.compile(bank_line.journal_id.name_pattern_bank_return).search(bank_line.name or '').string
            remittance_number = re.compile(bank_line.journal_id.remittance_pattern_bank_return).search(bank_line.remittance_number or '').string
            ref = re.compile(bank_line.journal_id.ref_pattern_bank_return).search(bank_line.ref or '').string
            note = re.compile(bank_line.journal_id.note_pattern_bank_return).search(bank_line.note or '').string
            date = datetime.strptime(bank_line.date, bank_line.journal_id.date_pattern_bank_return).strftime('%Y-%m-%d')

            if remittance_number == '' or date == '':
                raise except_orm('Warning',_('The current settings do not allow us to deduct the delivery number of this'
                                        'banking operation. Either this bank account is misconfigured in Odoo,'
                                        'or it is not a credit card transaction type'))
            journal_id = False
            self._cr.execute("""select sum(amount), journal_id from account_bank_statement_line \
                                where remittance_number=%s and date=%s and journal_id !=%s group by journal_id \
                                """, (remittance_number, date, bank_line.journal_id.id))
            terminal_line_ids = self._cr.fetchall()
            for terminal_line in terminal_line_ids:
                if terminal_line[0] == bank_line.amount:
                    if journal_id:
                        raise except_orm('Warning', _('Different journals found with this remittance number and this amount %s' % (str(terminal_line_ids))))
                    journal_id = terminal_line[1]
            if not journal_id:
                raise except_orm('Warning', _('Your bank statement indicates an amount of %s %s for the discount number %s.'
                                             'It is impossible to find a matching discount in our sales history' %
                                             (bank_line.amount, bank_line.journal_id.currency_id.symbol, remittance_number)))

            terminal_line_ids = self.search([('remittance_number', '=', remittance_number), ('date', '=', date),
                                             ('journal_id', '=', journal_id)])

            reconciled_statement = self.env['account.bank.statement'].search([('all_lines_reconciled', '=', True), ('line_ids', 'in', terminal_line_ids.ids)])
            if not reconciled_statement:
                raise except_orm('Warning', _('A statement is not reconciled %s' % (reconciled_statement.ids,)))

            self.reconcil_bank_statement_line(bank_line, remittance_number, terminal_line_ids[0].journal_id.default_credit_account_id.id)
            self.reconcil_account_move_line(bank_line, terminal_line_ids)
        return

    def reconcil_bank_statement_line(self, bank_line, remittance_number, account_id):
        move_line_data_credit = {
                'name': _('Remitance BC %s' % (remittance_number,)),
                'debit': 0.0,
                'credit': bank_line.amount,
                'journal_id': bank_line.journal_id.id,
                'date': bank_line.date,
                'account_id': account_id,
                }
        bank_line.process_reconciliation([], [], [move_line_data_credit])
        return

    def reconcil_account_move_line(self, bank_line, terminal_line_ids):
        account_id_ref = terminal_line_ids[0].journal_id.default_debit_account_id.id
        line_to_reconcil = []
        for statement_line in terminal_line_ids:
            for move in statement_line.statement_id.move_line_ids:
                if move.account_id.id == account_id_ref and move.id not in line_to_reconcil:
                    line_to_reconcil.append(move.id)
        for move in bank_line.statement_id.move_line_ids:
            if move.account_id.id == account_id_ref and move.id not in line_to_reconcil:
                line_to_reconcil.append(move.id)
        reconcil_obj = self.env['account.move.line.reconcile'].with_context(active_ids=line_to_reconcil)
        reconcil_obj.trans_rec_reconcile_full()
        return


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def payment_terminal_bank_launch(self, ):
        for line in self:
            line.line_ids.payment_terminal_bank_reconciliation()
        return
