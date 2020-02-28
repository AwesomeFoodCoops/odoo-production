
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_id = fields.Many2one('account.payment', 'Payment Entry')

    @api.multi
    def unmatch_bankstatement(self):
        for record in self:
            record.line_ids.write({'statement_line_id': False})

    @api.multi
    def unmatch_bankstatement_wizard(self):
        active_ids = self._context.get('active_ids', [])
        active_model = self._context.get('active_model', [])

        view_id = self.env.ref(
            'coop_account.view_unmatch_bank_statement_wizard_form')

        mess_confirm = _('Are you sure you want to unmatch %s transactions?') %\
            (len(active_ids))

        wizard = self.env['unmatch.bank.statement.wizard'].create({
            'mess_confirm': mess_confirm
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

    @api.multi
    def check_bank_statement_journal(self):
        for move in self:
            for line in move.line_ids:
                if not line.statement_id.journal_id.bank_account_id and \
                        line.account_id.reconciled_account:
                    raise UserError(_(
                        'You cannot reconcile that account move with ' +
                        'a bank statement line that is not related to bank journal.'))

    @api.multi
    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        self.check_bank_statement_journal()
        return res
