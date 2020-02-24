# -*- coding: utf-8 -*-
from openerp import api, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_expense_account_readonly = fields.Boolean(
        compute='_compute_is_account_readonly',
        help='Technical field',
    )

    is_income_account_readonly = fields.Boolean(
        compute='_compute_is_account_readonly',
        help='Technical field',
    )

    @api.onchange('categ_id', 'fiscal_classification_id')
    def _onchange_categ_fiscal_classification_id(self):
        res = super(
            ProductTemplate, self)._onchange_categ_fiscal_classification_id()
        if self.fiscal_classification_id:
            vals = {
                'property_account_income_id': False,
                'property_account_expense_id': False,
            }
            vals.update(self.get_fiscal_account(self.fiscal_classification_id))
            self.update(vals)
        return res

    @api.model
    def get_fiscal_account(self, fc=False):
        vals = {}
        if fc and isinstance(fc, int):
            fc = self.env['account.product.fiscal.classification'].browse(fc)
        if not fc:
            return vals
        if fc.income_account_id:
            vals.update({
                'property_account_income_id': fc.income_account_id.id})
        if fc.expense_account_id:
            vals.update({
                'property_account_expense_id': fc.expense_account_id.id})
        return vals

    @api.model
    def create(self, vals):
        if 'fiscal_classification_id' in vals:
            fiscal_classification_id = vals.get('fiscal_classification_id')
            account_vals = self.get_fiscal_account(fiscal_classification_id)
            vals.update(account_vals)
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'fiscal_classification_id' in vals:
            fiscal_classification_id = vals.get('fiscal_classification_id')
            account_vals = self.get_fiscal_account(fiscal_classification_id)
            vals.update(account_vals)
        return super(ProductTemplate, self).write(vals)

    @api.multi
    def toggle_available_in_pos(self):
        for rec in self:
            rec.available_in_pos = not rec.available_in_pos

    @api.multi
    @api.depends(
        'fiscal_classification_id.income_account_id',
        'fiscal_classification_id.expense_account_id',
    )
    def _compute_is_account_readonly(self):
        for rec in self:
            fc_id = rec.fiscal_classification_id
            rec.is_income_account_readonly = \
                fc_id and fc_id.income_account_id
            rec.is_expense_account_readonly = \
                fc_id and fc_id.expense_account_id
