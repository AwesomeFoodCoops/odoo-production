# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models
import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    scale_logo_code = fields.Char(
        related="product_tmpl_id.scale_logo_code",
        readonly=True,
        store=True)
    volume = fields.Float(digits=dp.get_precision('Volume'))
