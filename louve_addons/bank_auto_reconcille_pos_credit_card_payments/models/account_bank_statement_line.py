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

remittance_date = False
remittance_number = False

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def match_line(self, journal, line_name, line_ref, line_note):
        global remittance_date
        global remittance_number
        remittance_date = False
        remittance_number = False
        def extract_remittance_date(parser):
            global remittance_date
            if remittance_date:
                return
            try:
                res = parser.group("bank_remitance_date")
                remittance_date = datetime.strptime(res, journal.date_pattern_bank_return).strftime('%Y-%m-%d')
            except Exception:
                pass

        def extract_remittance_number(parser):
            global remittance_number
            if remittance_number:
                return
            try:
                remittance_number = parser.group("bank_remitance_number")
            except Exception:
                pass

        def parse_string(pattern, string):
            parser_search = re.compile(pattern).search(string)

            if parser_search == None:  # vérification des chaines desquelles ont ne soit rien extraires
                raise ValueError("The pattern does not match with the string : " + pattern + " => " + string)
                return False

            extract_remittance_date(parser_search)
            extract_remittance_number(parser_search)

        parse_string(journal.name_pattern_bank_return, line_name)
        parse_string(journal.ref_pattern_bank_return, line_ref)
        if line_note:
            parse_string(journal.note_pattern_bank_return, line_note)

        return remittance_date, remittance_number

    def match_charges_line(self, journal, line_name, line_ref, line_note):
        global remittance_number
        remittance_number = False

        def extract_remittance_number(parser):
            global remittance_number
            if remittance_number:
                return
            try:
                remittance_number = parser.group("bank_remitance_number")
            except Exception:
                pass

        def parse_string(pattern, string):
            parser_search = re.compile(pattern).search(string)

            if parser_search == None:  # vérification des chaines desquelles ont ne soit rien extraires
                raise ValueError("The pattern does not match with the string : " + pattern + " => " + string)
                return False

            extract_remittance_number(parser_search)

        parse_string(journal.name_charges_pattern_bank_return, line_name)
        parse_string(journal.ref_charges_pattern_bank_return, line_ref)
        if line_note:
            parse_string(journal.note_charges_pattern_bank_return, line_note)

        return remittance_number

    @api.multi
    def payment_terminal_bank_reconciliation(self):
        for bank_line in self:
            if bank_line.amount < 0:
                continue
            date, remittance_number = self.match_line(bank_line.journal_id, bank_line.name, bank_line.ref,
                                                      bank_line.note)

            if remittance_number == False or date == False:
                raise except_orm('Warning',
                                 _('The current settings do not allow us to deduct the delivery number of this'
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
                        raise except_orm('Warning', _(
                            'Different journals found with this remittance number and this amount %s' % (
                            str(terminal_line_ids))))
                    journal_id = terminal_line[1]
            if not journal_id:
                raise except_orm('Warning',
                                 _('Your bank statement indicates an amount of %s %s for the discount number %s.'
                                   'It is impossible to find a matching discount in our sales history' %
                                   (bank_line.amount, bank_line.journal_id.currency_id.symbol, remittance_number)))

            terminal_line_ids = self.search([('remittance_number', '=', remittance_number), ('date', '=', date),
                                             ('journal_id', '=', journal_id)])

            reconciled_statement = self.env['account.bank.statement'].search(
                [('all_lines_reconciled', '=', True), ('line_ids', 'in', terminal_line_ids.ids)])
            if not reconciled_statement:
                raise except_orm('Warning', _('A statement is not reconciled %s' % (reconciled_statement.ids,)))

            self.reconcil_bank_statement_line(bank_line, remittance_number,
                                              terminal_line_ids[0].journal_id.default_credit_account_id.id)
            self.reconcil_account_move_line(bank_line, terminal_line_ids)
            self.reconcil_chages_bank_statement_line(bank_line, remittance_number, date)
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
            for move in statement_line.journal_entry_ids.line_ids:
                if move.account_id.id == account_id_ref and move.id not in line_to_reconcil:
                    line_to_reconcil.append(move.id)
        for move in bank_line.statement_id.move_line_ids:
            if move.account_id.id == account_id_ref and move.id not in line_to_reconcil:
                line_to_reconcil.append(move.id)
        reconcil_obj = self.env['account.move.line.reconcile'].with_context(active_ids=line_to_reconcil)
        reconcil_obj.trans_rec_reconcile_full()
        return

    def reconcil_chages_bank_statement_line(self, bank_line, remittance_number, date):
        search_charges = self.search([('amount', '<', 0), ('date', '=', date),
                                      ('statement_id', '=', bank_line.statement_id.id)])
        charges_line_id = False
        for charges_line in search_charges:
            charges_remittance_number = self.match_charges_line(bank_line.journal_id, charges_line.name,
                                                                     charges_line.ref, charges_line.note)
            if charges_remittance_number == remittance_number:
                if charges_line_id:
                    raise except_orm('Warning', _(
                            'Different charges line found with this remittance number %s and this date %s' % (
                                remittance_number, date)))
                charges_line_id = charges_line
        move_line_data_credit = {
            'name': _('Remitance BC %s' % (remittance_number,)),
            'debit': charges_line_id.amount * -1,
            'credit': 0.0,
            'journal_id': bank_line.journal_id.id,
            'date': bank_line.date,
            'account_id': bank_line.journal_id.bank_charge_account_id.id,
        }
        charges_line_id.process_reconciliation([], [], [move_line_data_credit])
        return

class TerminalBankReconciliationReport(models.TransientModel):
    _name = 'terminal.reconciliation.report'

    name = fields.Text('Report', default=_("Waiting launch..."))

    @api.multi
    def payment_terminal_bank_launch(self):
        res_ok = 0
        res_nok = 0
        error_list = []
        for line in self.env['account.bank.statement.line'].browse(self._context['active_ids']):
            try:
                line.payment_terminal_bank_reconciliation()
                res_ok += 1
            except Exception, e:
                res_nok += 1
                if hasattr(e, 'value'):
                    error = e.value
                else:
                    error = e.message
                error = '%s %s \n' % (line.name, error)
                error_list.append(error)
        self.name = _(' %s reconciliation to do \n %s reconciliation ok \n %s reconciliation ko \n' % (
            len(self._context['active_ids']), res_ok, res_nok,))
        for error in error_list:
            self.name += error
        return {
            'name': _('Payment Terminal auto reconcil'),
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'terminal.reconciliation.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.ids[0],
        }
