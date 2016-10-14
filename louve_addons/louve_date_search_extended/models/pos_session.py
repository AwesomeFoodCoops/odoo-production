# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp import models, fields, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    search_year = fields.Char(
        string='Year (Search)', compute='_compute_date_search',
        multi='_date_search', store=True, index=True)

    search_month = fields.Char(
        string='Month (Search)', compute='_compute_date_search',
        multi='_date_search', store=True, index=True)

    search_day = fields.Char(
        string='Day (Search)', compute='_compute_date_search',
        multi='_date_search', store=True, index=True)

    @api.multi
    @api.depends('start_at')
    def _compute_date_search(self):
        date_scheme = '%Y-%m-%d %H:%M:%S'
        for item in self:
            if item.start_at:
                my_date = datetime.strptime(item.start_at, date_scheme)
                item.search_year = my_date.strftime('%Y')
                item.search_month = my_date.strftime('%Y-%m')
                item.search_day = my_date.strftime('%Y-%m-%d')
            else:
                item.search_year = False
                item.search_month = False
                item.search_day = False
