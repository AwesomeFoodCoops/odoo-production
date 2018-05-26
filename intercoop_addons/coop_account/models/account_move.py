# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_id = fields.Many2one('account.payment', 'Payment Entry')

    @api.multi
    def unmatch_bankstatement(self):
        for record in self:
            if record.statement_line_id:
                for line in record.line_ids:
                    if line.statement_id.line_ids and record.statement_line_id\
                            in line.statement_id.line_ids:
                        line.write({'statement_id': False})
                record.write({
                    'statement_line_id': False
                })
        return True

    @api.multi
    def check_bank_statement_journal(self):
        for move in self:
            if move.statement_line_id:
                journal =\
                    move.statement_line_id.statement_id.journal_id
                lines = move.line_ids
                if not journal.bank_account_id and \
                        any(line.account_id.reconciled_account for line in lines):
                    raise UserError(_(
                        'You cannot reconcile that account move with ' +
                        'a bank statement line that is not related to bank journal.'))

    @api.multi
    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        self.check_bank_statement_journal()
        return res
