# -*- coding: utf-8 -*-
from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def action_view_invoice(self):
        '''
        Modify the function to set default invoice journal as supplier
        journal
        '''
        res = super(PurchaseOrder, self).action_view_invoice()

        # Use the default Purchase Journal set in Partner for Invoice Journal
        default_journal = self.partner_id and self.partner_id and \
            self.partner_id.default_purchase_journal_id or False

        if default_journal:
            if res.get('context'):
                res['context']['default_journal_id'] = default_journal.id
            else:
                res['context'] = {'default_journal_id': default_journal.id}
        return res
