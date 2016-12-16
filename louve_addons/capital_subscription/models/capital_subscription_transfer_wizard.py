# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class CapitalSubscriptionTransferWizard(models.TransientModel):
    _name = 'capital.subscription.transfer.wizard'

    # Default Section
    def default_invoice_id(self):
        if self._context.get('active_model', False) == 'account.invoice':
            return self._context.get('active_id', False)

    # Column Section
    invoice_id = fields.Many2one(
        comodel_name='account.invoice', string='Invoice',
        required=True, default=default_invoice_id)

    date_transfer = fields.Date(string='Transfer Date', required=True)

    current_partner_id = fields.Many2one(
        comodel_name='res.partner', string='Current Partner',
        related='invoice_id.partner_id')

    new_partner_id = fields.Many2one(
        comodel_name='res.partner', string='New Partner', required=True)

    # Action Section
    @api.multi
    def button_confirm(self):
        assert len(self) == 1, "Incorrect call"

        imd_obj = self.env['ir.model.data']
        wizard = self[0]

        # Create new invoice
        new_invoice = wizard.invoice_id.copy()
        new_invoice.partner_id = wizard.new_partner_id
        new_invoice.date_invoice = wizard.date_transfer

        # Validate New Invoice, calling workflow
        new_invoice.signal_workflow('invoice_open')

        # Create refund invoice
        refund_invoice = wizard.invoice_id.refund(
            date_invoice=wizard.date_transfer, date=wizard.date_transfer,
            description=_('Capital transfer to %s (%s)' % (
                wizard.new_partner_id.name, new_invoice.name)))

        # Validate refund Invoice, calling workflow
        refund_invoice.signal_workflow('invoice_open')

        # Return tree view on the new invoices
        action = imd_obj.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd_obj.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd_obj.xmlid_to_res_id('account.invoice_form')

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
            'domain': "[('id','in',%s)]" % [new_invoice.id, refund_invoice.id],
        }
