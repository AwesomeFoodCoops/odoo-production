# -*- coding: utf-8 -*-

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    discount_computation = fields.Selection(
        selection=[('total', 'Total'), ('unit_price', 'Unit Price')],
        string="Discount Computation")
