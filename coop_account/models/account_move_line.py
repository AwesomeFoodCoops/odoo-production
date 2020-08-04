
import json
from odoo import api, models, fields, _
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    other_balance = fields.Monetary(
        string='Other Balance',
        default=0.0)
    search_year = fields.Char(
        string='Year (Search)', compute='_compute_date_search',
        multi='_date_search', store=True, index=True)
    search_month = fields.Char(
        string='Month (Search)', compute='_compute_date_search',
        multi='_date_search', store=True, index=True)
    search_day = fields.Char(
        string='Day (Search)', compute='_compute_date_search',
        multi='_date_search', store=True, index=True)

    @api.model
    def create(self, vals):
        debit = vals.get('debit', 0)
        credit = vals.get('credit', 0)
        vals.update({
            'other_balance': credit - debit,
        })
        return super(AccountMoveLine, self).create(vals)

    @api.multi
    def write(self, vals):
        self.calculate_orther_balance(vals)
        return super(AccountMoveLine, self).write(vals)

    @api.multi
    def calculate_orther_balance(self, vals):
        for record in self:
            if 'debit' in vals or 'credit' in vals:
                debit = vals.get('debit', record.debit)
                credit = vals.get('credit', record.credit)
                vals.update({
                    'other_balance': credit - debit,
                })
        return True

    @api.multi
    @api.constrains('move_id', 'account_id')
    def check_account_type_bank(self):
        for line in self:
            if line.move_id:
                line_account_bank = line.move_id.line_ids.filtered(
                    lambda a: a.account_id.reconciled_account)
                if len(line_account_bank) > 1:
                    raise UserError(_(
                        'Only one journal item on an account requiring ' +
                        'bank reconciliation can be booked in this ' +
                        'account move. It is impossible to add another ' +
                        'one. Please create a distinct account move to ' +
                        'registrer this account.move.line and its ' +
                        'counterpart.'))

    def _create_writeoff(self, vals):
        res = super(AccountMoveLine, self)._create_writeoff(vals)
        partner = self.mapped('partner_id')
        lines = res.mapped('move_id.line_ids')
        for line in lines:
            line.partner_id = partner.id if len(partner) == 1 and\
                not any(not line.partner_id for line in self)\
                else False
        return res

    @api.multi
    def unmatch_bankstatement_wizard(self):
        active_ids = self._context.get('active_ids', [])
        active_model = self._context.get('active_model', [])
        view_id = self.env.ref(
            'coop_account.view_unmatch_bank_statement_wizard_form')
        mess_confirm = _(
            'Are you sure you want to unmatch %s transactions?'
            ) % (len(active_ids))
        wizard = self.env['unmatch.bank.statement.wizard'].create({
            'mess_confirm': mess_confirm,
        })
        return {
            'name': _('Unmatch Bank Statement'),
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wizard.id,
            'res_model': 'unmatch.bank.statement.wizard',
            'target': 'new',
            'context': {'active_ids': active_ids, 'active_model': active_model}
        }

    @api.model
    def export_wrong_reconciliation_ml(self):
        wrong_reconciliation_ml_data = self.get_wrong_reconciliation_ml_data()
        data = {
            'model': self._name,
            'headers': wrong_reconciliation_ml_data['headers'],
            'rows': wrong_reconciliation_ml_data['rows']
        }
        return json.dumps(data)

    @api.model
    def get_wrong_reconciliation_ml_data(self):
        read_columns = [
            'name', 'journal_id', 'ref', 'date', 'partner_id', 'company_id',
            'check_holder_name', 'account_id', 'move_id', 'debit', 'credit',
            'quantity', 'statement_line_id', 'statement_id', 'payment_id',
            'check_deposit_id'
        ]
        model_fields = self._fields
        header_columns = [getattr(model_fields[column], 'string')
                          for column in read_columns]
        header_columns = ['External ID'] + header_columns
        read_columns = ['id'] + read_columns
        wrong_move_lines = self.get_wrong_reconciliation_ml()
        if not wrong_move_lines:
            raise UserError(_("Everything is ok. There's nothing to export."))
        record_values_dict = wrong_move_lines.export_data(read_columns)
        converted_data_rows = [
            [cell_data.encode('utf8') for cell_data in data_row]
            for data_row in record_values_dict['datas']
        ]
        return {
            'rows': converted_data_rows,
            'headers': header_columns,
        }

    @api.model
    def get_wrong_reconciliation_ml(self):
        wrong_move_lines = self
        selected_journals = self.env['account.journal'].search(
            [('export_wrong_reconciliation', '=', True)]
        )
        if not selected_journals:
            raise UserError(_(
                "Before using this feature, please select a few journals "
                "to analyze.\nGo to 'Accounting > Configuration > Journals' "
                "and enable the 'Export Wrong Reconciliation' checkbox."))
        self.env.cr.execute("""
            SELECT statement_line_id
            FROM account_move_line
            WHERE statement_line_id IS NOT NULL AND journal_id IN %s
            GROUP BY statement_line_id
            HAVING COUNT(statement_line_id) > 1
        """, (tuple(selected_journals.ids),))
        line_ids = [id_tuple[0] for id_tuple in self.env.cr.fetchall()]
        bank_statement_line_ids = \
            self.env['account.bank.statement.line'].browse(line_ids)
        for stml in bank_statement_line_ids:
            move_line_ids = stml.journal_entry_ids
            move_ids = move_line_ids.mapped('move_id')
            if len(move_ids) == 1 and len(move_line_ids) == 2:
                continue
            for aml in move_line_ids.filtered(lambda ml: not ml.statement_id):
                if (
                    aml.date.year <= stml.date.year
                    and aml.date.month <= stml.date.month
                ):
                    continue
                else:
                    wrong_move_lines |= aml
        return wrong_move_lines

    @api.multi
    @api.depends('date')
    def _compute_date_search(self):
        """ Merge from date_search_extended module from version 9
        remove date_search_extended module from version 12"""
        for rec in self:
            if rec.date:
                rec.search_year = rec.date.strftime('%Y')
                rec.search_month = rec.date.strftime('%Y-%m')
                rec.search_day = rec.date.strftime('%Y-%m-%d')
            else:
                rec.search_year = False
                rec.search_month = False
                rec.search_day = False
