# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class CapitalFundraisingCategory(models.Model):
    _inherit = 'capital.fundraising.category'

    # Column Section
    is_default = fields.Boolean(string='Is default')

    is_part_A = fields.Boolean(
        string='Is Part A', help="If checked, partner that have subscribed"
        " such fundraising category will belong to 'Type A subscriptor'"
        " category")
