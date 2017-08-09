# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.invoice.refund"

    @api.model
    def _get_reason(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
            if inv.is_capital_fundraising:
                return _('Redemption %s - %d') % \
                    (inv.number, inv.partner_id.barcode_base)
        return super(AccountInvoiceRefund, self)._get_reason()

    description = fields.Char(default=_get_reason)
