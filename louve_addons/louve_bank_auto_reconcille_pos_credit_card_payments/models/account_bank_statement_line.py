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
        for line in self:
            name = re.compile(line.journal_id.name_pattern_bank_return).search(line.ref or '').string
            remittance_number = re.compile(line.journal_id.remittance_pattern_bank_return).search(line.remittance_number or '').string
            memo = re.compile(line.journal_id.memo_pattern_bank_return).search(line.name or '').string
            note = re.compile(line.journal_id.note_pattern_bank_return).search(line.note or 'qsdqd').string
            date = datetime.strptime(line.date, line.journal_id.date_pattern_bank_return).strftime('%Y-%m-%d')

            if name == '' or remittance_number == '' or memo == '' or note == '' or date == '':
                raise except_orm('Warning',_('The current settings do not allow us to deduct the delivery number of this'
                                        'banking operation. Either this bank account is misconfigured in Odoo,'
                                        'or it is not a credit card transaction type'))
            journal_id = False
            self._cr.execute("""select sum(amount), journal_id from account_bank_statement_line \
                                where remittance_number=%s and date=%s and journal_id !=%s group by journal_id \
                                """, (remittance_number, date, line.journal_id.id))

            search_lines = self._cr.fetchall()
            for search_line in search_lines:
                if search_line[0] == line.amount:
                    if journal_id:
                        raise except_orm('Warning',_('Too many journal found with this remittance number for this amount %s' % (str(search_lines))))
                    journal_id = search_line[1]
            if not journal_id:
                raise except_orm('Warning',_('Your bank statement indicates an amount of %s € for the discount number %s.'
                                        'It is impossible to find a matching discount in our sales history' %
                                      (line.amount, remittance_number)))

            search_lines = self.search([('remittance_number', '=', remittance_number), ('date', '=', date),
                                        ('journal_id', '=', journal_id)])

            reconciled_statement = self.env['account.bank.statement'].search([('all_lines_reconciled', '=', True), ('line_ids', 'in', search_lines.ids)])
            if reconciled_statement:
               raise except_orm('Warning',_('A statement is reconciled %s' % (reconciled_statement.ids,)))

            move_line_data_credit = {
                'name': _('Remitance BC %s' % (remittance_number,)),
                'debit': 0.0,
                'credit': line.amount,
                'journal_id': line.journal_id.id,
                'date': line.date,
                'account_id': search_lines[0].journal_id.default_credit_account_id.id,
                }
            line.process_reconciliation([], [], [move_line_data_credit])
        return


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def payment_terminal_bank_launch(self, ):
        for line in self:
            line.line_ids.payment_terminal_bank_reconciliation()
        return
