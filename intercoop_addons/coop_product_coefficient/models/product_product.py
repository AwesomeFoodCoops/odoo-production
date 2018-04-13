# -*- coding: utf-8 -*-
# Copyright (C) 2015-Today: Smile (<http://www.smile.fr>)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Custom Section
    @api.multi
    def recompute_base_price(self):
        self.product_tmpl_id._compute_base_price()
