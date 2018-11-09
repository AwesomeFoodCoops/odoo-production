# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import UserError
from datetime import timedelta
from openerp.osv import expression


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
            'name': _(' Reconcile'),
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'bank.statement.line.reconcile.wizard',
            'target': 'new',
            'context': {'line_ids': line_ids}
        }

    """
    Override native method to check date_month of payment account move line 
    when processing bank statement line
    """
    @api.multi
    def process_reconciliation(self, counterpart_aml_dicts=None,
                               payment_aml_rec=None, new_aml_dicts=None):
        self.ensure_one()
        if not self.check_payment_aml_date_month(payment_aml_rec):
            raise UserError(_('You cannot reconcile with an account.move posterior to the transaction date except if you reconcile the transaction with only one account move.'))
        return super(AccountBankStatementLine, self).process_reconciliation(
            counterpart_aml_dicts, payment_aml_rec, new_aml_dicts)


    """
    Make sure all payment account move lines month 
    less than or equal to the current month of bank statement line 
    """
    @api.multi
    def check_payment_aml_date_month(self, payment_aml_rec):
        self.ensure_one()
        result = True
        if len(payment_aml_rec) > 1:
            statement_line_date = fields.Date.from_string(self.date)
            for payment_aml in payment_aml_rec:
                payment_aml_date = fields.Date.from_string(payment_aml.date)
                if not (payment_aml_date.year <= statement_line_date.year and
                        payment_aml_date.month <= statement_line_date.month):
                    result = False
                    break
        return result
