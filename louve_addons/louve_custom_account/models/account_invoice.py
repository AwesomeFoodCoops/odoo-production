# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def merge_lines(self):
        for invoice in self:
            if invoice.state != 'draft':
                # Not merge invoice line when invoice != draft
                raise Warning(_('You can only merge draft invoice!'))
            # Only merge invoice line when invoice at state draft
            to_delete_ids = []
            itered_ids = []
            for line in invoice.invoice_line_ids:
                itered_ids.append(line.id)
                line_to_merge = invoice.invoice_line_ids.search([
                    ('invoice_id', '=', invoice.id),
                    ('discount', '=', line.discount),
                    ('price_unit', '=', line.price_unit),
                    ('product_id', '=', line.product_id.id),
                    ('account_id', '=', line.account_id.id),
                    ('account_analytic_id', '=', line.account_analytic_id.id),
                    ('id', 'not in', itered_ids)], limit=1)
                if line_to_merge:
                    to_delete_ids.append(line.id)
                    line_to_merge.write({
                        'quantity': line_to_merge.quantity + line.quantity,
                        'origin': (line_to_merge.origin or
                                   '') + (line.origin or '')})
            invoice.write({
                'invoice_line_ids': [
                    (2, id_delete) for id_delete in to_delete_ids
                ]
            })
