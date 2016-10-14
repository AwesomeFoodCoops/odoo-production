# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class CapitalFundraisingCategoryLine(models.Model):
    _name = 'capital.fundraising.category.line'

    minimum_share_qty = fields.Integer(
        string='Minimum Share Quantity', required=True, default=1)

    fundraising_partner_type_id = fields.Many2one(
        comodel_name='capital.fundraising.partner.type',
        string='Fundraising Partner Type', required=True)

    fundraising_category_id = fields.Many2one(
        comodel_name='capital.fundraising.category', string='Category',
        required=True)
