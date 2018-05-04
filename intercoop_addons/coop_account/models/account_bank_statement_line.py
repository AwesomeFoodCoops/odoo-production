# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import UserError
from datetime import timedelta
from openerp.osv import expression


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def _prepare_reconciliation_move(self, move_name):
        vals = super(AccountBankStatementLine,
                     self)._prepare_reconciliation_move(move_name)
        # reset name as '/' to allow Post function in account.move
        # use sequence of journal when posting account.move entry
        vals.update({
            'name': '/'
        })
        return vals

    @api.multi
    def get_statement_line_reconcile(self):
        if any(line.journal_entry_ids for line in self):
            raise UserError(_(
                'This wizzard is only available on non reconcilled' +
                ' bank statement lines. Please unselect already' +
                ' reconcilled lines.'))
        view_id = self.env.ref(
            'coop_account.view_bank_statement_line_reconcile_wizard_form')
        line_ids = self._context.get('active_ids', [])

        return {
            'name': _('Reconcile'),
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'bank.statement.line.reconcile.wizard',
            'target': 'new',
            'context': {'line_ids': line_ids}
        }

    # Overload Section
    def get_move_lines_for_reconciliation(
            self, excluded_ids=None, str=False, offset=0, limit=None,
            additional_domain=None, overlook_partner=False):
        additional_domain = self.get_date_additional_domain(additional_domain)
        return super(
            AccountBankStatementLine, self).get_move_lines_for_reconciliation(
                excluded_ids=excluded_ids, str=str, offset=offset, limit=limit,
                additional_domain=additional_domain,
                overlook_partner=overlook_partner)

    def get_date_additional_domain(self, additional_domain):
        date_string = fields.Date.from_string(self.date)
        search_limit_days = self.statement_id and \
            self.statement_id.journal_id and \
            self.statement_id.journal_id.search_limit_days or 0.0
        if date_string and search_limit_days:
            limit_days_after = date_string + timedelta(
                days=search_limit_days)
            limit_days_before = date_string - timedelta(
                days=search_limit_days)
            domain = [('date', '<', limit_days_after),
                      ('date', '>', limit_days_before)]
            additional_domain = expression.AND([additional_domain, domain])
        return additional_domain
