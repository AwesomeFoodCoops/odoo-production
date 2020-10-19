# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import Warning as UserError
from openerp.tools.safe_eval import safe_eval


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    # POS Payments
    cb_parent_id = fields.Many2one(
        'account.journal', 'CB Parent')

    cb_child_ids = fields.One2many(
        'account.journal', 'cb_parent_id', string='CB Childs')

    cb_lines_domain = fields.Char(
        "CB Lines Domain",
        help="Domain that identifies the credit card lines",
    )

    cb_delta_days = fields.Integer('CB Delta Days', default=3)
    cb_rounding = fields.Float("CB Rounding", default=0.01)
    cb_contactless_matching = fields.Boolean("CB Contactless Matching")
    cb_contactless_lines_domain = fields.Char(
        "Contactless Lines Domain",
        help="Domain that identifies the contactless lines",
    )
    cb_contactless_delta_days = fields.Integer(
        'Contactless Delta Days',
        help='Delta days between the regular line date '
             'and the contactless line date.',
        default=0,
    )

    # Charges
    bank_expense_name_pattern = fields.Char()
    bank_expense_ref_pattern = fields.Char()
    bank_expense_note_pattern = fields.Char()

    bank_expense_account_id = fields.Many2one(
        'account.account', 'Bank Expense Account')

    @api.constrains('cb_lines_domain')
    def _check_cb_lines_domain(self):
        for rec in self:
            try:
                domain = safe_eval(rec.cb_lines_domain or '[]')
                self.env['account.bank.statement.line'].search(domain, limit=1)
            except Exception as e:
                raise UserError(str(e))

    @api.constrains('cb_contactless_lines_domain')
    def _check_cb_contactless_lines_domain(self):
        for rec in self:
            try:
                domain = safe_eval(rec.cb_contactless_lines_domain or '[]')
                self.env['account.bank.statement.line'].search(domain, limit=1)
            except Exception as e:
                raise UserError(str(e))
