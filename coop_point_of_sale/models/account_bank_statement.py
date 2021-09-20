# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    total_entry_encoding_sales = fields.Monetary(
        'Sale Transactions Subtotal', compute='_compute_total_entries',
        help="Total of sale transaction lines.")
    total_entry_encoding_cash = fields.Monetary(
        'Cash Moves', compute='_compute_total_entries',
        help="Total of cash inputs or outputs.")

    @api.multi
    @api.depends(
        'line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real')
    def _compute_total_entries(self):
        for abst in self:
            abst.total_entry_encoding_sales = sum(
                [line.amount for line in abst.line_ids
                    if line.pos_statement_id])
            abst.total_entry_encoding_cash = sum(
                [line.amount for line in abst.line_ids
                    if not line.pos_statement_id])
