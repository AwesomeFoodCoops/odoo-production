# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    # Column Section
    is_capital_fundraising = fields.Boolean(
        string='Used for Capital Fundraising', default=True)
