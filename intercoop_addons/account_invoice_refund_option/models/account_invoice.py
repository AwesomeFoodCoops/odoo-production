# -*- coding: utf-8 -*-


from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None,
            date=None, description=None, journal_id=None):
        context = dict(self._context or {})
        res = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice,
            date=date, description=description, journal_id=journal_id)
        invoice_lines = context.get('invoice_lines', [])
        if invoice_lines:
            res['invoice_line_ids'] = self._refund_cleanup_lines(
                invoice_lines)
        return res

    @api.multi
    @api.returns('self')
    def refund(
            self, date_invoice=None, date=None,
            description=None, journal_id=None):
        context = dict(self._context or {})
        res = super(AccountInvoice, self).refund(
            date_invoice=date_invoice,
            date=date, description=description, journal_id=journal_id)
        invoice_lines = context.get('invoice_lines', [])
        if invoice_lines:
            res._onchange_invoice_line_ids()
        return res
