# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountProductFiscalClassification(models.Model):
    _inherit = 'account.product.fiscal.classification'

    income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
    )
    expense_account_id = fields.Many2one(
        'account.account',
        string='Expense Account',
    )
    # Make tax required
    sale_tax_ids = fields.Many2many(required=True)
    purchase_tax_ids = fields.Many2many(required=True)
