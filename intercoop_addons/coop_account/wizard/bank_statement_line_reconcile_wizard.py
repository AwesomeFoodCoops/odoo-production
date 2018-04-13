# -*- coding: utf-8 -*-


from openerp import models, fields, api


class BankStatementLineReconcileWizard(models.TransientModel):
    _name = 'bank.statement.line.reconcile.wizard'
    _description = 'Bank Statement Line Reconcile Wizard'

    account_id = fields.Many2one('account.account', "Account", required=True)

    @api.multi
    def bank_statement_line_reconcile(self):
        self.ensure_one()
        line_ids = self._context.get('line_ids', False)
        lines = self.env['account.bank.statement.line'].browse(line_ids)
        for line in lines:
            if line.state == 'open':
                vals = {
                    'name': line.name,
                    'debit': line.amount < 0 and -line.amount or 0.0,
                    'credit': line.amount > 0 and line.amount or 0.0,
                    'account_id': self.account_id.id}
                line.process_reconciliation(new_aml_dicts=[vals])
        return True
