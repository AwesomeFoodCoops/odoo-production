# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import Warning
import copy


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

    @api.model
    def _default_refund_quantity(self):
        AccountInvoice = self.env['account.invoice']
        active_id = self._context.get('active_id', False)
        if not active_id:
            return 0.0
        origin_inv = AccountInvoice.browse(active_id)
        qty = sum([line.quantity for line in origin_inv.invoice_line_ids if \
                   line.product_id and line.product_id.is_capital_fundraising])
        return qty

    description = fields.Char(default=_get_reason)
    refund_quantity = fields.Integer(string="Quantity Of Shares To Refund",
                                     default=_default_refund_quantity,
                                     required=True)

    @api.constrains('refund_quantity')
    def _check_refund_quantity_is_positive(self):
        AccountInvoice = self.env['account.invoice']
        active_id = self._context.get('active_id', False)
        if not active_id:
            return True
        origin_inv = AccountInvoice.browse(active_id)
        if origin_inv.is_capital_fundraising and self.refund_quantity <= 0:
            raise Warning("Error! The refund quantity must be greater than 0.")
        return True

    @api.multi
    def compute_refund(self, mode='refund'):
        self.ensure_one()
        AccountInvoice = self.env['account.invoice']
        res = super(AccountInvoiceRefund, self).compute_refund(mode)
        if mode == 'refund':
            domain = isinstance(res, dict) and copy.deepcopy(res.get('domain',
                                                                     []))
            domain.append(tuple(['fundraising_category_id', '!=', False]))
            if domain:
                invs = AccountInvoice.search(domain)
                invs.apply_refund_deficit_share(self.refund_quantity)
        return res

