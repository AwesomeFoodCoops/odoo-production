# -*- coding: utf-8 -*-
##############################################################################
#
#    POS Payment Terminal module for Odoo
#    Copyright (C) 2014 Aurélien DUMAINE
#    Copyright (C) 2015 Akretion (www.akretion.com)
#    Copyright (C) 2017 Iván Todorovich <ivan.todorovich@druidoo.io>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    # POS Payments
    cb_parent_id = fields.Many2one(
        'account.journal', 'CB Parent')

    cb_child_ids = fields.One2many(
        'account.journal', 'cb_parent_id', string='CB Childs')

    cb_contract_number = fields.Char('CB Contact Number')

    cb_delta_days = fields.Integer('CB Delta Days', default=3)
    cb_rounding = fields.Float("CB Rounding", default=0.01)
    cb_contactless_matching = fields.Boolean("CB Contactless Matching")
    cb_contract_number_contactless = fields.Char('Contactless Contract Number')
    cb_contactless_delta_days = fields.Integer('CB Delta Days', default=0)

    # Charges
    bank_expense_name_pattern = fields.Char()
    bank_expense_ref_pattern = fields.Char()
    bank_expense_note_pattern = fields.Char()

    bank_expense_account_id = fields.Many2one(
        'account.account', 'Bank Expense Account')
