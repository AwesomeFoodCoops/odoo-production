# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    CONFIRM_FUNDRAISING_PAYMENT_SELECTION = [
        ('allways', 'Allways'),
        ('yes', 'Yes by Default'),
        ('no', 'No by Default'),
        ('never', 'Never'),
    ]

    # Column Section
    is_capital_fundraising = fields.Boolean(
        string='Used for Capital Fundraising', default=False)

    confirm_fundraising_payment = fields.Selection(
        string='Confirm Fundraising Payments', default='yes',
        selection=CONFIRM_FUNDRAISING_PAYMENT_SELECTION, help="Setting"
        " for the payment in the wizard that create Subscriptions.\n"
        " * Allways : Payment is allways confirmed\n"
        " * Yes : Payment confirmed by default\n"
        " * No : Payment not confirmed by default\n"
        " * Never : Payment is never confirmed")
