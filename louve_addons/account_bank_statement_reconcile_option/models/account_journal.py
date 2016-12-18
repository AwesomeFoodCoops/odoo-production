# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    _SELECTION_RECONCILE_MODE = [
        ('normal', 'Normal'),
        ('journal_account', 'Journal Accounts'),
    ]

    # Column Section
    reconcile_mode = fields.Selection(
        selection=_SELECTION_RECONCILE_MODE, default='normal', required=True,
        string='Reconciliation Mode', help="Change the reconciliation"
        " proposition.\n"
        " 'Normal': default behaviour of Odoo;\n"
        " 'Journal Accounts', reconciliation wizard will propose only account"
        " move lines with accounts defined in debit / credit accounting"
        " setting of the current journal.")
