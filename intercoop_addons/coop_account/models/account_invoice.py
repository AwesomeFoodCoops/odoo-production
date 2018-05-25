# -*- coding: utf-8 -*-

from openerp import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_date_assign(self):
        for inv in self:
            if not inv.date_due:
                inv._onchange_payment_term_date_invoice()
        return True
