# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    search_limit_days = fields.Integer(
        string='Search Limit Days', default=0
    )
