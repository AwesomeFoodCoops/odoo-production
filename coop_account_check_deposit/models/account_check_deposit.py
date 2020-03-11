from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountCheckDeposit(models.Model):
    _inherit = "account.check.deposit"

    name = fields.Char(
        required=True,
        states={
            'done': [('readonly', '=', True)]
        },
    )
    destination_journal_id = fields.Many2one(
        'account.journal',
        string="Destination Journal",
        states={'done': [('readonly', '=', True)]},)

    @api.model
    def _prepare_account_move_vals(self, deposit):
        if not deposit.destination_journal_id:
            return super()._prepare_account_move_vals(deposit)
        date = deposit.deposit_date
        if deposit.destination_journal_id.sequence_id:
            move_name =\
                deposit.destination_journal_id.sequence_id.with_context(
                    ir_sequence_date=date).next_by_id()
        else:
            raise UserError(_(
                'Please define a sequence on the destination journal.'))
        move_vals = {
            'journal_id': deposit.destination_journal_id.id,
            'date': date,
            'name': move_name,
            'ref': deposit.name,
        }
        return move_vals

    @api.model
    def _prepare_move_line_vals(self, line, deposit):
        # replace assert is raise
        if line.debit <= 0:
            raise UserError(_(
                'Debit must have a value'))
        res = super()._prepare_move_line_vals(line)
        res['name'] = _('%s - Ref. Check %s') % \
            (deposit.name, line.ref or line.name or '')
        return res

    @api.model
    def _prepare_counterpart_move_lines_vals(
            self, deposit, total_debit, total_amount_currency):
        res = super()._prepare_counterpart_move_lines_vals(
            deposit, total_debit, total_amount_currency)
        if deposit.destination_journal_id:
            account = deposit.destination_journal_id.default_debit_account_id
            res['account_id'] = account.id
        return res

    def validate_deposit(self):
        am_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        for deposit in self:
            move_vals = self._prepare_account_move_vals(deposit)
            move = am_obj.create(move_vals)
            total_debit = 0.0
            total_amount_currency = 0.0
            to_reconcile_lines = []
            for line in deposit.check_payment_ids:
                total_debit += line.debit
                total_amount_currency += line.amount_currency
                line_vals = self._prepare_move_line_vals(line, deposit)
                line_vals['move_id'] = move.id
                move_line = move_line_obj.with_context(
                    check_move_validity=False).create(line_vals)
                to_reconcile_lines.append(line + move_line)

            # Create counter-part
            if (
                    deposit.destination_journal_id and
                    not deposit.destination_journal_id
                    .default_debit_account_id):
                raise UserError(
                    _("Default Debit Account is not set on journal '%s'") %
                    deposit.destination_journal_id.name)

            # Create counter-part
            counter_vals = self._prepare_counterpart_move_lines_vals(
                deposit, total_debit, total_amount_currency)
            counter_vals['move_id'] = move.id
            move_line_obj.create(counter_vals)
            if deposit.company_id.check_deposit_post_move:
                move.post()

            deposit.write({'state': 'done', 'move_id': move.id})
            for reconcile_lines in to_reconcile_lines:
                reconcile_lines.reconcile()
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    state_deposit = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')], string='State Deposit',
        compute='_compute_state_deposit',
        help="Technical fields use invisible button 'DELETE'"
        "if state is draft button visible else button invisible")
    check_holder_name = fields.Char(string="Cheque Holder")

    @api.multi
    def _compute_state_deposit(self):
        for record in self:
            if not record.check_deposit_id:
                record.state_deposit = 'draft'
            else:
                record.state_deposit = record.check_deposit_id.state

    @api.multi
    def delete_check_payment(self):
        self.ensure_one()
        self.write({'check_deposit_id': False})
        return True

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        change_check_holder_name = self._context.get(
            'change_check_holder_name', False)
        if self.partner_id and not self.check_holder_name:
            if change_check_holder_name or self.check_deposit_id:
                self.check_holder_name = self.partner_id.name_get()[0][1] or ''

    @api.model
    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        res.update_check_holder_name()
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        self.update_check_holder_name()
        return res

    @api.multi
    def update_check_holder_name(self):
        '''
            Update check holder name for item was generate from deposit
        '''
        for record in self:
            if record.check_deposit_id and record.partner_id and not\
                    record.check_holder_name:
                record.check_holder_name = record.partner_id.name_get()[
                    0][1] or ''
            elif not record.check_deposit_id and record.check_holder_name:
                record.check_holder_name = ""
