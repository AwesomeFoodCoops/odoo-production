# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models
import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    scale_logo_code = fields.Char(
        related="product_tmpl_id.scale_logo_code",
        string="Scale Logo Code",
        readonly=True,
        store=True)
    volume = fields.Float(digits=dp.get_precision('Volume'))
