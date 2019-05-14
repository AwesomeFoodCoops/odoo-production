# -*- coding: utf-8 -*-
##############################################################################
#
#    POS Payment Terminal module for Odoo
#    Copyright (C) 2014 Aurélien DUMAINE
#    Copyright (C) 2015 Akretion (www.akretion.com)
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
import re


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def _match_bank_expense(self):
        self.ensure_one()
        matches = False
        for field in ['name', 'ref', 'note']:
            pattern = getattr(
                self.journal_id, 'bank_expense_%s_pattern' % field, False)
            if pattern:
                if re.compile(pattern).search(getattr(self, field)):
                    matches = True
                else:
                    return False
        return matches

    @api.multi
    def _reconcile_bank_expense(self):
        for line in self.filtered(lambda l: not l.journal_entry_ids):
            if line._match_bank_expense():
                if not line.journal_id.bank_expense_account_id:
                    raise UserError(_(
                        'You need to set a Bank Expense Account in the '
                        'journal if you want to use this feature.'))
                move_line_data_credit = {
                    'name': line.name,
                    'debit': line.amount * -1 if line.amount < 0.00 else 0.00,
                    'credit': line.amount if line.amount > 0.00 else 0.00,
                    'journal_id': line.journal_id.id,
                    'date': line.date,
                    'account_id': line.journal_id.bank_expense_account_id.id,
                }
                line.process_reconciliation([], [], [move_line_data_credit])
