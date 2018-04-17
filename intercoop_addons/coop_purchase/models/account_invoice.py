# -*- coding: utf-8 -*-

from openerp import api, models
from lxml import etree
from openerp.osv.orm import setup_modifiers


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        res = super(AccountInvoice, self).purchase_order_change()
        for line in self.invoice_line_ids:
            suppliers = line.product_id.seller_ids.filtered(
                lambda x: x.name == self.partner_id)
            if suppliers:
                line.base_price = suppliers[0].base_price
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}

        res = super(AccountInvoice, self).fields_view_get(cr, uid,
                                                          view_id=view_id,
                                                          view_type=view_type,
                                                          context=context,
                                                          toolbar=toolbar,
                                                          submenu=submenu)

        # Read only field contact base specific groups
        account_advise = self.user_has_groups(cr, uid,
                                              'account.group_account_manager')
        doc = etree.fromstring(res['arch'])
        if not account_advise:
            if view_type == 'form':
                list_readonly_field = ['journal_id', 'account_id', 'user_id',
                                       'payment_term_id', 'fiscal_position_id',
                                       'move_id', 'date',
                                       'company_id']
                for node in doc.xpath("//field"):
                    if node.get('name') in list_readonly_field:
                        node.set('readonly', '1')
                        setup_modifiers(node)
            res['arch'] = etree.tostring(doc)

        return res
