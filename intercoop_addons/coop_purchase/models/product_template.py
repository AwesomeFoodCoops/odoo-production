# -*- coding: utf-8 -*-
from openerp import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('categ_id', 'fiscal_classification_id')
    def _onchange_categ_fiscal_classification_id(self):
        res = super(
            ProductTemplate, self)._onchange_categ_fiscal_classification_id()
        if self.fiscal_classification_id:
            fiscal_account_values = self.get_fiscal_account(
                self.fiscal_classification_id
            )
            self.update(fiscal_account_values)
        return res

    @api.model
    def get_fiscal_account(self, fiscal_classification_id=False):
        fiscal_account_values = {
            'property_account_income_id': False,
            'property_account_expense_id': False,
        }
        if fiscal_classification_id:
            if isinstance(fiscal_classification_id, int):
                fiscal_classification_id = \
                    self.env['account.product.fiscal.classification'].browse(
                        fiscal_classification_id
                    )
            fiscal_account_values = {
                'property_account_income_id':
                    fiscal_classification_id.income_account_id.id,
                'property_account_expense_id':
                    fiscal_classification_id.expense_account_id.id,
            }
        return fiscal_account_values

    @api.model
    def create(self, vals):
        if 'fiscal_classification_id' in vals:
            fiscal_classification_id = vals.get('fiscal_classification_id', False)
            fiscal_account_values = self.get_fiscal_account(
                fiscal_classification_id)
            vals.update(fiscal_account_values)
        return super(ProductTemplate, self).create(vals=vals)

    @api.multi
    def write(self, vals):
        if 'fiscal_classification_id' in vals:
            fiscal_classification_id = vals.get('fiscal_classification_id',
                                                False)
            fiscal_account_values = self.get_fiscal_account(
                fiscal_classification_id)
            vals.update(fiscal_account_values)
        return super(ProductTemplate, self).write(vals=vals)
