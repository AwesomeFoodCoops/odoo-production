# -*- coding: utf-8 -*-

from openerp import api, models, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    @api.depends('asset_category_id', 'invoice_id.date_invoice')
    def _get_asset_date(self):
        super(AccountInvoiceLine, self)._get_asset_date()
        cat = self.asset_category_id
        if cat:
            if self.invoice_id.date_invoice:
                start_date = datetime.strptime(
                    self.invoice_id.date_invoice, DF)
                self.asset_start_date = start_date.strftime(DF)
