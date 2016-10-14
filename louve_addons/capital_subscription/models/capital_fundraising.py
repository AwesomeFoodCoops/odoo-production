# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class CapitalFundraising(models.Model):
    _name = 'capital.fundraising'

    name = fields.Char(string='Name')

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id.id)

    share_value = fields.Float(string='Share Value')

    category_ids = fields.One2many(
        string='Categories', comodel_name='capital.fundraising.category',
        inverse_name='fundraising_id')

    journal_id = fields.Many2one(
        comodel_name='account.journal', string='Journal', required=True,
        domain="[('type', '=', 'sale')]")
