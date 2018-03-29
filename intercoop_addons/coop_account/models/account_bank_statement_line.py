# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def _prepare_reconciliation_move(self, move_name):
        vals = super(AccountBankStatementLine,
                     self)._prepare_reconciliation_move(move_name)
        # reset name as '/' to allow Post function in account.move
        # use sequence of journal when posting account.move entry

        statement_line_name = self._context.get('statement_line_name', False)
        if statement_line_name:
            vals.update({
                'name': statement_line_name
            })
        else:
            vals.update({
                'name': '/'
            })
        return vals

    @api.multi
    def get_statement_line_reconcile(self):
        if any(line.journal_entry_ids for line in self):
            raise UserError(_(
                'This wizzard is only available on non reconcilled' +
                ' bank statement lines. Please unselect already' +
                ' reconcilled lines.'))
        view_id = self.env.ref(
            'coop_account.view_bank_statement_line_reconcile_wizard_form')
        line_ids = self._context.get('active_ids', [])

        return {
            'name': _('Reconcile'),
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'bank.statement.line.reconcile.wizard',
            'target': 'new',
            'context': {'line_ids': line_ids}
        }
