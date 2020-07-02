# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today Druidoo (<info@druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    # POS Payments
    cb_parent_id = fields.Many2one(
        'account.journal', 'CB Parent')

    cb_child_ids = fields.One2many(
        'account.journal', 'cb_parent_id', string='CB Childs')

    cb_lines_domain = fields.Char(
        "CB Lines Domain",
        help="Domain that identifies the credit card lines",
    )

    cb_delta_days = fields.Integer('CB Delta Days', default=3)
    cb_rounding = fields.Float("CB Rounding", default=0.01)
    cb_contactless_matching = fields.Boolean("CB Contactless Matching")
    cb_contactless_lines_domain = fields.Char(
        "Contactless Lines Domain",
        help="Domain that identifies the contactless lines",
    )
    cb_contactless_delta_days = fields.Integer(
        'Contactless Delta Days',
        help='Delta days between the regular line date '
             'and the contactless line date.',
        default=0,
    )

    # Charges
    bank_expense_name_pattern = fields.Char()
    bank_expense_ref_pattern = fields.Char()
    bank_expense_note_pattern = fields.Char()

    bank_expense_account_id = fields.Many2one(
        'account.account', 'Bank Expense Account')
