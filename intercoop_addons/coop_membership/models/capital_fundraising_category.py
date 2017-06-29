# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class CapitalFundraisingCategory(models.Model):
    _inherit = 'capital.fundraising.category'

    # Column Section
    is_default = fields.Boolean(string='Is default')

    minimum_share_qty = fields.Integer(
        string='Default Minimum qty')

    line_ids = fields.One2many(string='Exception rules for minimum qty')

    is_worker_capital_category = fields.Boolean(
        string="Is Worker Capital Category")
