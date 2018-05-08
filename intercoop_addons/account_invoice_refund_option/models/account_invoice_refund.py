# -*- coding: utf-8 -*-

from openerp import api, fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.model
    def _get_domain_invoice_line(self):
        invoice_id = self._context.get('active_id', False)
        return [('invoice_id', '=', invoice_id)]

    filter_refund = fields.Selection(
        selection_add=[('refund_select_product',
                        'Select product(s) for refunding')])
    invoice_line_ids = fields.Many2many(
        'account.invoice.line',
        string='Invoice Lines',
        domain=_get_domain_invoice_line)

    @api.multi
    def compute_refund(self, mode='refund'):
        if self.filter_refund == 'refund_select_product':
            self = self.with_context(invoice_lines=self.invoice_line_ids or [])
        return super(AccountInvoiceRefund, self).compute_refund(mode=mode)

    @api.onchange('filter_refund')
    def onchange_select_product(self):
        if self.filter_refund != 'refund_select_product':
            self.invoice_line_ids = []
