# -*- coding: utf-8 -*-
from openerp import models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def _prepare_reconciliation_move(self, move_name):
        vals = super(AccountBankStatementLine,
                     self)._prepare_reconciliation_move(move_name)
        # reset name as '/' to allow Post function in account.move
        # use sequence of journal when posting account.move entry
        vals.update({
            'name': '/'
        })
        return vals
