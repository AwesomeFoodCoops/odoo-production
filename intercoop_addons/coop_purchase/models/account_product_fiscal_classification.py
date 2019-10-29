# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountProductFiscalClassification(models.Model):
    _inherit = 'account.product.fiscal.classification'

    # Make fields required
    sale_tax_ids = fields.Many2many(required=True)
    purchase_tax_ids = fields.Many2many(required=True)
