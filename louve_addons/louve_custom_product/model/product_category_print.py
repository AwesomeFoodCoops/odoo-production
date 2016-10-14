# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductCategoryprint(models.Model):
    _inherit = 'product.category.print'

    @api.model
    def _get_default_model(self):
        return self.env['pricetag.model'].search([], limit=1)

    pricetag_model_id = fields.Many2one(
        'pricetag.model', 'Pricetag Model', required=True,
        default=lambda s: s._get_default_model())
