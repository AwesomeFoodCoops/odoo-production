# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_capital_fundraising = fields.Boolean(
        string='Concerns Capital Fundraising', help=" Check this box"
        " if you want to use this product for capital fundraising.\n"
        " If yes, please check accounting and fiscal settings.")

    is_part_A = fields.Boolean(
        string='Is type A', help=" Check this box"
        " if this product is a type A capital subscription.")

    @api.multi
    @api.onchange('is_capital_fundraising')
    def onchange_is_capital_fundraising(self):
        for template in self:
            if not template.is_capital_fundraising:
                template.is_part_A = False
