# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today Druidoo (<info@druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import models, api, _
from odoo.exceptions import UserError


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
