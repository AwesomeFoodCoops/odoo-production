# -*- coding: utf-8 -*-
###############################################################################
#
#   account_check_deposit for Odoo
#   Copyright (C) 2012-2016 Akretion (http://www.akretion.com/)
#   @author: Benoît GUILLOT <benoit.guillot@akretion.com>
#   @author: Chafique DELLI <chafique.delli@akretion.com>
#   @author: Alexis de Lattre <alexis.delattre@akretion.com>
#   @author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
###############################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.exceptions import Warning as UserError


class AccountCheckDeposit(models.Model):
    _name = "account.check.deposit"
    _description = "Account Check Deposit"
    _order = 'deposit_date desc'

    @api.multi
    @api.depends(
        'company_id', 'currency_id', 'check_payment_ids.debit',
        'check_payment_ids.amount_currency',
        'move_id.line_ids.reconciled')
    def _compute_check_deposit(self):
        for deposit in self:
            total = 0.0
            count = 0
            reconcile = False
            currency_none_same_company_id = False
            if deposit.company_id.currency_id != deposit.currency_id:
                currency_none_same_company_id = deposit.currency_id.id
            for line in deposit.check_payment_ids:
                count += 1
                if currency_none_same_company_id:
                    total += line.amount_currency
                else:
                    total += line.debit
            if deposit.move_id:
                for line in deposit.move_id.line_ids:
                    if line.debit > 0 and line.reconciled:
                        reconcile = True
            deposit.total_amount = total
            deposit.is_reconcile = reconcile
            deposit.currency_none_same_company_id =\
                currency_none_same_company_id
            deposit.check_count = count

    name = fields.Char(string='Name', required=True,
                       states={'done': [('readonly', '=', True)]},)
    check_payment_ids = fields.One2many(
        'account.move.line', 'check_deposit_id', string='Check Payments',
        states={'done': [('readonly', '=', True)]})
    deposit_date = fields.Date(
        string='Deposit Date', required=True,
        states={'done': [('readonly', '=', True)]},
        default=fields.Date.context_today)
    journal_id = fields.Many2one(
        'account.journal', string='Journal', domain=[('type', '=', 'bank')],
        required=True, states={'done': [('readonly', '=', True)]})
    destination_journal_id = fields.Many2one(
        'account.journal',
        string="Destination Journal",
        required=True, states={'done': [('readonly', '=', True)]},)
    journal_default_account_id = fields.Many2one(
        'account.account', related='journal_id.default_debit_account_id',
        string='Default Debit Account of the Journal', readonly=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        states={'done': [('readonly', '=', True)]})
    currency_none_same_company_id = fields.Many2one(
        'res.currency', compute='_compute_check_deposit',
        string='Currency (False if same as company)')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('done', 'Done'),
        ], string='Status', default='draft', readonly=True)
    move_id = fields.Many2one(
        'account.move', string='Journal Entry', readonly=True)
    partner_bank_id = fields.Many2one(
        'res.partner.bank', string='Bank Account',
        related="destination_journal_id.bank_account_id", readonly=True)
    line_ids = fields.One2many(
        'account.move.line', related='move_id.line_ids',
        string='Lines', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        states={'done': [('readonly', '=', True)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'account.check.deposit'))
    total_amount = fields.Float(
        compute='_compute_check_deposit',
        string="Total Amount", readonly=True,
        digits=dp.get_precision('Account'))
    check_count = fields.Integer(
        compute='_compute_check_deposit', readonly=True,
        string="Number of Checks")
    is_reconcile = fields.Boolean(
        compute='_compute_check_deposit', readonly=True,
        string="Reconcile")

    @api.multi
    @api.constrains('currency_id', 'check_payment_ids', 'company_id')
    def _check_deposit(self):
        for deposit in self:
            deposit_currency = deposit.currency_id
            if deposit_currency == deposit.company_id.currency_id:
                for line in deposit.check_payment_ids:
                    if line.currency_id:
                        raise ValidationError(
                            _("The check with amount %s and reference '%s' "
                                "is in currency %s but the deposit is in "
                                "currency %s.") % (
                                line.debit, line.ref or '',
                                line.currency_id.name,
                                deposit_currency.name))
            else:
                for line in deposit.check_payment_ids:
                    if line.currency_id != deposit_currency:
                        raise ValidationError(
                            _("The check with amount %s and reference '%s' "
                                "is in currency %s but the deposit is in "
                                "currency %s.") % (
                                line.debit, line.ref or '',
                                line.currency_id.name,
                                deposit_currency.name))

    @api.multi
    def unlink(self):
        for deposit in self:
            if deposit.state == 'done':
                raise UserError(
                    _("The deposit '%s' is in valid state, so you must "
                        "cancel it before deleting it.")
                    % deposit.name)
        return super(AccountCheckDeposit, self).unlink()

    @api.multi
    def backtodraft(self):
        for deposit in self:
            if deposit.move_id:
                # It will raise here if journal_id.update_posted = False
                deposit.move_id.button_cancel()
                for line in deposit.check_payment_ids:
                    if line.reconciled:
                        line.remove_move_reconcile()
                deposit.move_id.unlink()
            deposit.write({'state': 'draft'})
        return True

    @api.model
    def _prepare_account_move_vals(self, deposit):
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
        # assert (line.debit > 0), 'Debit must have a value'
        return {
            'name': _('%s - Ref. Check %s') % (deposit.name,
                                               line.ref or line.name or ''),
            'credit': line.debit,
            'debit': 0.0,
            'account_id': line.account_id.id,
            'partner_id': line.partner_id.id,
            'currency_id': line.currency_id.id or False,
            'amount_currency': line.amount_currency * -1.0,
        }

    @api.model
    def _prepare_counterpart_move_lines_vals(
            self, deposit, total_debit, total_amount_currency):
        account = deposit.destination_journal_id.default_debit_account_id
        return {
            'name': deposit.name,
            'debit': total_debit,
            'credit': 0.0,
            'account_id': account.id,
            'partner_id': False,
            'currency_id': deposit.currency_none_same_company_id.id or False,
            'amount_currency': total_amount_currency,
        }

    @api.multi
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
            if not deposit.destination_journal_id.default_debit_account_id:
                raise UserError(
                    _("Default Debit Account is not set on journal '%s'") %
                    deposit.destination_journal_id.name)

            counter_vals = self._prepare_counterpart_move_lines_vals(
                deposit, total_debit, total_amount_currency)
            counter_vals['move_id'] = move.id
            move_line_obj.create(counter_vals)

            move.post()
            deposit.write({'state': 'done', 'move_id': move.id})
            # We have to reconcile after post()
            for reconcile_lines in to_reconcile_lines:
                reconcile_lines.reconcile()
        return True

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            partner_banks = self.env['res.partner.bank'].search(
                [('company_id', '=', self.company_id.id)])
            if len(partner_banks) == 1:
                self.partner_bank_id = partner_banks[0]
        else:
            self.partner_bank_id = False

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            if self.journal_id.currency_id:
                self.currency_id = self.journal_id.currency_id
            else:
                self.currency_id = self.journal_id.company_id.currency_id


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    check_deposit_id = fields.Many2one(
        'account.check.deposit', string='Check Deposit', copy=False)
    state_deposit = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')], string='State Deposit',
        compute='compute_state_deposit',
        help="Technical fields use invisible button 'DELETE'"
        "if state is draft button visible else button invisible")
    check_holder_name = fields.Char(string="Cheque Holder")        

    @api.multi
    def compute_state_deposit(self):
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
        if self.partner_id:
            self.check_holder_name = self.partner_id.name_get()[0][1] or ''

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id', False)
        check_holder_name = vals.get('check_holder_name', False)
        partner = self.env['res.partner'].browse(partner_id)
        if partner and not check_holder_name:
            vals.update({
                'check_holder_name': partner.name_get()[0][1] or ''
            })
        return super(AccountMoveLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'partner_id' in vals and 'check_holder_name' not in vals:
            partner_id = vals.get('partner_id', False)
            for record in self:
                partner = self.env['res.partner'].browse(partner_id)
                if partner:
                    vals.update({
                        'check_holder_name': partner.name_get()[0][1] or ''
                    })
        return super(AccountMoveLine, self).write(vals)
