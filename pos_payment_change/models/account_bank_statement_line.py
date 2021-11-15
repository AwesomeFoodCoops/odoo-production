# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright since 2009 Trobz (<https://trobz.com/>).
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

from odoo import api, fields, models
from odoo.tools import float_is_zero, pycompat


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.multi
    def cash_draw_statement_line(self):
        move_list = []
        already_done_stmt_line_ids = [a['statement_line_id'][0] for a in self.env['account.move.line'].read_group([('statement_line_id', 'in', self.ids)], ['statement_line_id'], ['statement_line_id'])]
        managed_st_line = []
        for st_line in self:
            # Technical functionality to automatically reconcile by creating a new move line
            if st_line.account_id and not st_line.id in already_done_stmt_line_ids:
                managed_st_line.append(st_line.id)
                # Create move and move line vals
                move_vals = st_line._prepare_reconciliation_move(st_line.statement_id.name)
                aml_dict = {
                    'name': st_line.name,
                    'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                    'credit': st_line.amount > 0 and st_line.amount or 0.0,
                    'account_id': st_line.account_id.id,
                    'partner_id': st_line.partner_id.id,
                    'statement_line_id': st_line.id,
                }
                st_line._prepare_move_line_for_currency(aml_dict, st_line.date or fields.Date.context_today())
                move_vals['line_ids'] = [(0, 0, aml_dict)]
                balance_line = st_line._prepare_reconciliation_move_line(
                    move_vals, -aml_dict['debit'] if st_line.amount < 0 else aml_dict['credit'])
                # Replace the account
                if st_line.journal_id.type == 'cash' and st_line.journal_id.change_account_id:
                    balance_line.update({
                        'account_id': st_line.journal_id.change_account_id.id
                    })

                move_vals['line_ids'].append((0, 0, balance_line))
                move_list.append(move_vals)

        # Creates
        move_ids = self.env['account.move'].create(move_list)
        move_ids.post()

        for move, st_line in pycompat.izip(move_ids, self.browse(managed_st_line)):
            st_line.write({'move_name': move.name})

    @api.multi
    def cash_change_statement_line(self):
        self.ensure_one()
        st_line = self
        if not st_line.journal_id.change_account_id:
            return
        move_list = []
        total = st_line.amount * -1  # Important
        account_type_receivable = self.env.ref('account.data_account_type_receivable')
        # Create move and move line vals
        move_vals = st_line._prepare_reconciliation_move(st_line.statement_id.name)
        aml_dict = {
            'name': st_line.name,
            'debit': total < 0 and -total or 0.0,
            'credit': total > 0 and total or 0.0,
            'account_id': st_line.journal_id.change_account_id.id,
            'partner_id': st_line.partner_id.id,
            'statement_line_id': st_line.id,
        }
        st_line._prepare_move_line_for_currency(aml_dict, st_line.date or fields.Date.context_today())
        move_vals['line_ids'] = [(0, 0, aml_dict)]
        balance_line = st_line._prepare_reconciliation_move_line(
            move_vals, -aml_dict['debit'] if total < 0 else aml_dict['credit'])
        move_vals['line_ids'].append((0, 0, balance_line))
        move_list.append(move_vals)

        # Creates
        move_ids = self.env['account.move'].create(move_list)
        move_ids.post()

        for move, st_line in pycompat.izip(move_ids, st_line):
            st_line.write({'move_name': move.name})

    @api.multi
    def cash_change_counterpart_creation(self):
        """
        """
        payment_list = []
        move_list = []
        account_type_receivable = self.env.ref('account.data_account_type_receivable')
        already_done_stmt_line_ids = [a['statement_line_id'][0] for a in self.env['account.move.line'].read_group([('statement_line_id', 'in', self.ids)], ['statement_line_id'], ['statement_line_id'])]
        managed_st_line = []
        total = 0.0
        st_line = None
        for line in self:
            if not line.account_id or line.id in already_done_stmt_line_ids:
                continue
            managed_st_line.append(line)
            total += line.amount
            if line.amount > 0:
                st_line = line
        if not managed_st_line or not st_line:
            return
        payment_methods = (total > 0) and st_line.journal_id.inbound_payment_method_ids or st_line.journal_id.outbound_payment_method_ids
        currency = st_line.journal_id.currency_id or st_line.company_id.currency_id
        partner_type = 'customer' if st_line.account_id.user_type_id == account_type_receivable else 'supplier'
        payment_list.append({
            'payment_method_id': payment_methods and payment_methods[0].id or False,
            'payment_type': total > 0 and 'inbound' or 'outbound',
            'partner_id': st_line.partner_id.id,
            'partner_type': partner_type,
            'journal_id': st_line.statement_id.journal_id.id,
            'payment_date': st_line.date,
            'state': 'reconciled',
            'currency_id': currency.id,
            'amount': abs(total),
            'communication': st_line._get_communication(payment_methods[0] if payment_methods else False),
            'name': st_line.statement_id.name or _("Bank Statement %s") % st_line.date,
        })

        # Create move and move line vals
        move_vals = st_line._prepare_reconciliation_move(st_line.statement_id.name)
        aml_dict = {
            'name': st_line.name,
            'debit': total < 0 and -total or 0.0,
            'credit': total > 0 and total or 0.0,
            'account_id': st_line.account_id.id,
            'partner_id': st_line.partner_id.id,
            'statement_line_id': st_line.id,
        }
        st_line._prepare_move_line_for_currency(aml_dict, st_line.date or fields.Date.context_today())
        move_vals['line_ids'] = [(0, 0, aml_dict)]
        balance_line = st_line._prepare_reconciliation_move_line(
            move_vals, -aml_dict['debit'] if total < 0 else aml_dict['credit'])
        move_vals['line_ids'].append((0, 0, balance_line))
        move_list.append(move_vals)

        # Creates
        payment_ids = self.env['account.payment'].create(payment_list)
        for payment_id, move_vals in pycompat.izip(payment_ids, move_list):
            for line in move_vals['line_ids']:
                line[2]['payment_id'] = payment_id.id
        move_ids = self.env['account.move'].create(move_list)
        move_ids.post()

        for move, payment in pycompat.izip(move_ids, payment_ids):
            payment.write({'payment_reference': move.name})

        for line in managed_st_line:
            line.cash_change_statement_line()
