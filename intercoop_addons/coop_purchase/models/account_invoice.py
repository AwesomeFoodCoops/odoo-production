# -*- coding: utf-8 -*-

from openerp import api, models, _
from openerp.exceptions import Warning
from lxml import etree
from openerp.osv.orm import setup_modifiers


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if self.purchase_id:
            self.check_received_product(self.purchase_id)
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

    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_purchase_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        result = super(AccountInvoice, self)._onchange_allowed_purchase_ids()
        if self.type == 'in_refund':
            if result['domain']['purchase_id']:
                result['domain']['purchase_id'][0] =\
                    ('invoice_status', 'in', ('to invoice', 'invoiced'))
        return result

    @api.model
    def create(self, vals):
        purchase_id_val = vals.get('purchase_id', False)
        if purchase_id_val:
            purchase_id = self.env['purchase.order'].browse(purchase_id_val)
            self.check_received_product(purchase_id)
        res = super(AccountInvoice, self).create(vals)
        return res

    @api.model
    def check_received_product(self, purchase_id):
        for line in purchase_id.order_line:
            product_id = line.product_id
            purchase_method = product_id.purchase_method
            received_qty = line.qty_received
            if purchase_method == 'receive' and not received_qty:
                raise Warning(_('Please confirm reception before creating an invoice for this PO'))

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountInvoice, self).\
            _prepare_invoice_line_from_po_line(line)
        if self.type == 'in_refund':
            qty_invoiced = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.invoice_id.state not in ['cancel']:
                    if inv_line.invoice_id.type == 'in_invoice' \
                            and inv_line.invoice_id.state == 'paid':
                        qty_invoiced += inv_line.uom_id._compute_qty_obj(
                            inv_line.uom_id,
                            inv_line.quantity,
                            line.product_uom
                        )
                    elif inv_line.invoice_id.type == 'in_refund' \
                            and inv_line.invoice_id.state == 'paid':
                        qty_invoiced -= inv_line.uom_id._compute_qty_obj(
                            inv_line.uom_id,
                            inv_line.quantity,
                            line.product_uom
                        )
            # get invoiced qty
            data.update({
                'quantity': qty_invoiced
            })
        return data
