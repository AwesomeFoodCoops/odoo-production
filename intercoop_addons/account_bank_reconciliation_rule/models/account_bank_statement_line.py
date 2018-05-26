# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, fields, _


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.multi
    def get_data_for_reconciliation_widget(self, excluded_ids=None):
        '''
        Override this method to transfer current journal by context
        '''

        # Get currnent journal
        journal_ids = self.mapped('journal_id').ids

        self = self.with_context(journal_ids=journal_ids)

        return super(AccountBankStatementLine,
                     self).get_data_for_reconciliation_widget(excluded_ids)

    @api.multi
    def get_move_lines_for_reconciliation_widget(
            self, excluded_ids=None, str=False, offset=0, limit=None):
        '''
        Override this method to transfer current journal by context
        '''

        # Get currnent journal
        journal_ids = self.mapped('journal_id').ids

        self = self.with_context(journal_ids=journal_ids)

        return super(AccountBankStatementLine,
            self).get_move_lines_for_reconciliation_widget(
            excluded_ids, str, offset, limit)
