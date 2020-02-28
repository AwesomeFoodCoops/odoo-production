
from odoo import api, models, fields, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    account_move_ids = fields.One2many(
        'account.move', 'payment_id', 'Journals Entry')
    state = fields.Selection(selection_add=[('cancelled', 'Cancelled')])
    partner_code = fields.Integer(
        related='partner_id.barcode_base', store=True)
    operation_type = fields.Selection([
        ('sepa_debit', 'SEPA Direct Debit'),
        ('sepa_credit', 'SEPA Direct Credit'),
        ('check', 'Check'),
        ('credit_card', 'Credit card'),
        ('lcr', 'LCR'),
        ('other', 'Other')], string='Operation Type')
    text_check_code = fields.Text(string='Check Code')
    text_lcr_code = fields.Text(string='LCR Code')

    def _create_payment_entry(self, amount):
        move = super(AccountPayment, self)._create_payment_entry(amount)
        move.payment_id = self.id
        return move

    @api.onchange('operation_type')
    def onchange_operation_type(self):
        invoice = self.invoice_ids[0] or False
        communication = ''
        if invoice:
            communication = invoice.reference or invoice.name or invoice.number
        if self.operation_type != 'check':
            self.text_check_code = ''
        if self.operation_type != 'lcr':
            self.text_lcr_code = ''
        if self.operation_type == 'sepa_debit':
            self.communication = communication + \
                '-' + _('SEPA Direct Debit')
        if self.operation_type == 'sepa_credit':
            self.communication = communication + \
                '-' + _('SEPA Direct Credit')
        if self.operation_type == 'credit_card':
            self.communication = communication + \
                '-' + _('Credit Card ')
        if self.operation_type == 'other':
            self.communication = communication

    @api.onchange('text_check_code', 'text_lcr_code')
    def onchange_memo_based_on_operation_type(self):
        invoice = self.invoice_ids[0] or False
        communication = ''
        if invoice:
            communication = invoice.reference or invoice.name or invoice.number
        if self.text_check_code:
            check_nb = _('Check nb ')
            self.communication = '%s-%s%s' %\
                (communication, check_nb, self.text_check_code)
        if self.text_lcr_code:
            lcr_nb = _('LCR nb ')
            self.communication = '%s-%s%s' %\
                (communication, lcr_nb, self.text_lcr_code)

    @api.multi
    def reverse_payments(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx.update({
            'active_ids': self.account_move_ids.ids,
            'payment_id': self.id,
        })
        return {
            'name': _('Reverse Moves'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move.reversal',
            'view_id': self.env.ref(
                'account.view_account_move_reversal').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def re_generate(self, default=None):
        self.ensure_one()
        new_record = super(AccountPayment, self).copy(default=default)
        new_record.invoice_ids = self.invoice_ids
        return {
            'name': _('Draft Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'view_id': self.env.ref(
                'AccountPayment_transfer_account.view_AccountPayment_form_extend').id,
            'type': 'ir.actions.act_window',
            'res_id': new_record.id
        }
