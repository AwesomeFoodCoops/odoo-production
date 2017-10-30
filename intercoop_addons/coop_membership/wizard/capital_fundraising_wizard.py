# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class CapitalFundraisingWizard(models.TransientModel):
    _inherit = 'capital.fundraising.wizard'

    def default_can_change_fundraising_category(self):
        return self.user_has_groups(
            'coop_membership.subscriptions_can_change_fundraising_category')

    can_change_fundraising_category = fields.Boolean(
        string="Can Change fundraising Category",
        default=default_can_change_fundraising_category)
