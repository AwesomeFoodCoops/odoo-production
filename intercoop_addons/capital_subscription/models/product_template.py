# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_capital_fundraising = fields.Boolean(
        string='Concerns Capital Fundraising', help=" Check this box"
        " if you want to use this product for capital fundraising.\n"
        " If yes, please check accounting and fiscal settings.")

    is_deficit_product = fields.Boolean(
        string='Deficit Product', help=" Check this box"
        " if you want to use this product for Capital Fundraising Deficit.")

    deficit_share_account_id = fields.Many2one('account.account',
                                               string="Deficit Share Account")
