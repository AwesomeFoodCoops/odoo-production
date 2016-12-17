# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    # Column Section
    simple_reconcile = fields.Boolean(
        string='Simple Reconciliation', help="Check this box if you"
        " want to reduce reconciliation proposition.\n"
        " If checked, reconciliation wizard will propose only account"
        " move lines of the current journal accounts")
