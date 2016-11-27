# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountMoveLineReconcileWriteoff(models.TransientModel):
    _inherit = 'account.move.line.reconcile.writeoff'

    date_p = fields.Date(default=False)
    comment = fields.Char(default="")

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.writeoff_acc_id = self.journal_id.default_debit_account_id
