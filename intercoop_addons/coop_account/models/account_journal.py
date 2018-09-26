# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    search_limit_days = fields.Integer(
        string='Search Limit Days',
        help="Set here the number of days before and after the bank " +
        "transaction on which Journal Items can be proposed for reconciliation",
        default=0
    )
