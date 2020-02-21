from odoo import api, fields, models


class BankReconciliationSummaryWizard(models.TransientModel):
    _name = 'bank.reconciliation.summary.wizard'
    _description = 'Bank Reconciliation Summary Wizard'

    journal_id = fields.Many2one(
        'account.journal', "Journal",
        domain=[('type', '=', 'bank')],
        required=True
    )
    analysis_date = fields.Date(required=True)

    @api.multi
    def print_report(self, data):
        report_name = 'account_bank_statement_reconciliation_report' \
                      '.bank_reconciliation_summary_xlsx'
        return self.env.ref(report_name).report_action(self, data=data)
