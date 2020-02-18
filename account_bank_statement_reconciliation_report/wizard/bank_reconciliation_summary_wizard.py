# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BankReconciliationSummaryWizard(models.TransientModel):
    _name = 'bank.reconciliation.summary.wizard'
    _description = 'Bank Reconciliation Summary Wizard'

    journal_id = fields.Many2one(
        'account.journal', "Journal",
        domain=[('type', '=', 'bank')], required=True)
    analysis_date = fields.Date('Analysis Date', required=True)

    @api.multi
    def print_report(self, data):
        report_name = 'bank_reconciliation_summary_xlsx'
        return self.env['report'].get_action(self, report_name, data=data)
