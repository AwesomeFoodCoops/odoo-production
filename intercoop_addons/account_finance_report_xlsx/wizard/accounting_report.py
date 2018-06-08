# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, fields


class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"

    def _print_report(self, data):
        format_report = self.env.user.company_id.format_report_finance
        if format_report == 'xlsx':
            data['form'].update(
                self.read([
                    'date_from_cmp', 'debit_credit', 'date_to_cmp',
                    'filter_cmp', 'account_report_id', 'enable_filter',
                    'label_filter', 'target_move'])[0]
            )
            res = self.env['report'].get_action(
                self, 'report_account_financial_xlsx', data=data)

            data['ids'] = self.ids
            data['context'] = self._context

            res.update({
                'datas': data,
            })
            return res
        else:
            return super(AccountingReport, self)._print_report(data)
