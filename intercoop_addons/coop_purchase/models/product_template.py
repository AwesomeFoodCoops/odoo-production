# -*- coding: utf-8 -*-
from openerp import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('categ_id', 'fiscal_classification_id')
    def _onchange_categ_fiscal_classification_id(self):
        res = super(
            ProductTemplate, self)._onchange_categ_fiscal_classification_id()
        if self.fiscal_classification_id:
            update_vals = {
                'property_account_income_id':
                    self.fiscal_classification_id.income_account_id.id,
                'property_account_expense_id':
                    self.fiscal_classification_id.expense_account_id.id,
            }
        else:
            update_vals = {
                'property_account_income_id': False,
                'property_account_expense_id': False,
            }
        self.update(update_vals)
        return res
