# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountProductFiscalClassification(models.Model):
    _inherit = 'account.product.fiscal.classification'

    income_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Income Account',
        required=True
    )
    expense_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Expense Account',
        required=True
    )
    sale_tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='fiscal_classification_sale_tax_rel',
        column1='fiscal_classification_id', column2='tax_id',
        required=True
    )
    purchase_tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='fiscal_classification_purchase_tax_rel',
        column1='fiscal_classification_id', column2='tax_id',
        required=True
    )
