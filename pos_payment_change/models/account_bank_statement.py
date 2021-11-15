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


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def confirm_bank_cash_change(self):
        self.ensure_one()
        neg_st_lines = self.line_ids.filtered(
            lambda l: l.amount < 0.0 and l.pos_statement_id)
        pos_orders = []
        for line in neg_st_lines:
            if line.pos_statement_id.id in pos_orders:
                continue
            pos_orders.append(line.pos_statement_id.id)
            lines = self.line_ids.filtered(
                lambda l: line.pos_statement_id == l.pos_statement_id and \
                    line.account_id == l.account_id and \
                    line.journal_id == l.journal_id)
            if not lines:
                continue
            lines.cash_change_counterpart_creation()

    @api.multi
    def button_confirm_bank(self):
        self._balance_check()
        statements = self.filtered(lambda r: r.state == 'open')
        for statement in statements:
            journal = statement.journal_id
            if journal.type == 'cash' and journal.change_account_id:
                neg_st_lines = statement.line_ids.filtered(
                    lambda l: l.amount < 0.0 and l.pos_statement_id)

                if neg_st_lines:
                    statement.confirm_bank_cash_change()

                cashdraw_lines = statement.line_ids.filtered(
                    lambda l: not l.pos_statement_id)
                if cashdraw_lines:
                    cashdraw_lines.cash_draw_statement_line()

        super(AccountBankStatement, self).button_confirm_bank()
