# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, fields, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.v8
    def prepare_move_lines_for_reconciliation_widget(
            self, target_currency=False, target_date=False):
        '''      
        Override this function to change the logic of doing bank reconcliation:
        - if account_code of account.move.line = account_code of bank.statement.line  => the transaction is matched,
        - if account_code of account.move.line != account_code of bank.statement.line => a new move is generated,
          move.line on source account is allocated and counterpart
          on bank journal account is matched to the statement.
        '''

        res = super(AccountMoveLine,
                    self).prepare_move_lines_for_reconciliation_widget(
            target_currency, target_date)

        # Get current journal account and accounts
        journal_ids = self._context.get('journal_ids', [])
        journals = self.env['account.journal'].browse(journal_ids)
        debit_account = journals.mapped('default_debit_account_id')

        list_account_code = debit_account.mapped('code')

        # Update already paid if statement line with not account debit/credit
        # in current journal
        # if account_code of account.move.line = account_code of bank.statement.line  => only match 2 bank statement.line 
        # and account.move.line
        # if account_code of account.move.line != account_code of bank.statement.line => a new move is generated

        for line_data in res:
            if line_data['account_code'] in list_account_code:
                line_data.update({
                    'already_paid': True})
            else:
                line_data.update({
                    'already_paid': False})
        return res
