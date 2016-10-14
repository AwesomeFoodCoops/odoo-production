# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class CapitalFundraisingWizard(models.TransientModel):
    _name = 'capital.fundraising.wizard'

    def default_partner_id(self):
        if self._context.get('active_model', False) == 'res.partner':
            return self._context.get('active_id', False)

    # Column Section
    date_invoice = fields.Date(
        string='Invoice Date', required=True,
        default=fields.Date.context_today)

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner', required=True,
        default=default_partner_id)

    fundraising_partner_type_ids = fields.Many2many(
        comodel_name='capital.fundraising.partner.type',
        string='Fundraising Partner Type',
        related='partner_id.fundraising_partner_type_ids')

    share_qty = fields.Integer(string='Shares Quantity')

    category_id = fields.Many2one(
        comodel_name='capital.fundraising.category', string='Category',
        required=True)

    payment_journal_id = fields.Many2one(
        comodel_name='account.journal', string='Payment Method',
        domain="[('is_capital_fundraising', '=', True)]")

    confirm_fundraising_payment = fields.Selection(
        related='payment_journal_id.confirm_fundraising_payment')

    confirm_payment = fields.Boolean(
        string='Confirm Payment', help="Check this box to confirm the"
        " payment(s). In that case, the second account move will be"
        " written to transfer amount from unpaid account to paid account")

    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term', string='Payment Term',
        domain="[('is_capital_fundraising', '=', True)]", required=True)

    # On change section
    @api.onchange('partner_id', 'category_id')
    def onchange_partner_category(self):
        if self.partner_id and self.category_id:
            to_order_qty = self.category_id.check_minimum_qty(self.partner_id)
            self.share_qty = max(1, to_order_qty)

    @api.onchange('payment_journal_id')
    def onchange_payment_journal_id(self):
        if self.payment_journal_id:
            self.confirm_payment =\
                self.confirm_fundraising_payment in ['allways', 'yes']
        else:
            self.confirm_payment = False

    # Action Section
    @api.multi
    def button_confirm(self):
        assert len(self) == 1, "Incorrect call"

        imd_obj = self.env['ir.model.data']
        invoice_obj = self.env['account.invoice']
        payment_obj = self.env['account.payment']
        wizard = self[0]
        product = wizard.category_id.product_id
        invoice_vals = invoice_obj.default_get(invoice_obj._fields.keys())
        invoice_vals.update({
            'type': 'out_invoice',
            'date_invoice': wizard.date_invoice,
            'journal_id': wizard.category_id.fundraising_id.journal_id.id,
            'account_id': wizard.category_id.partner_account_id.id,
            'payment_term_id': wizard.payment_term_id.id,
            'partner_id': wizard.partner_id.id,
            'is_capital_fundraising': True,
            'fundraising_category_id': wizard.category_id.id,
            'invoice_line_ids': [[0, False, {
                'uom_id': product.uom_id.id,
                'product_id': product.id,
                'price_unit': product.lst_price,
                'name': product.name,
                'quantity': wizard.share_qty,
                'account_id': product.property_account_income_id.id}]],
        })

        # Create new invoice
        invoice = invoice_obj.create(invoice_vals)
        invoice.onchange_fundraising_category_id()

        # Validate Invoice, calling workflow
        invoice.signal_workflow('invoice_open')

        # Mark Payment
        payment_methods = wizard.category_id.fundraising_id.journal_id.\
            inbound_payment_method_ids

        if wizard.payment_journal_id:
            # create one payment per line in the account move just created,
            # to have correct date
            for move_line in invoice.move_id.line_ids.filtered(
                    lambda r: r.debit != 0).sorted(
                        key=lambda r: r.date_maturity):
                vals = {
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': wizard.partner_id.id,
                    'payment_method_id': payment_methods[0].id,
                    'journal_id': wizard.payment_journal_id.id,
                    'amount': move_line.debit,
                    'payment_date': move_line.date_maturity,
                    'communication': invoice.number,
                    'invoice_ids': [(4, invoice.id, None)],
                }
                payment = payment_obj.create(vals)
                if wizard.confirm_payment:
                    payment.post()

        # Return view on the new invoice
        action = imd_obj.xmlid_to_object('account.action_invoice_tree1')
        form_view_id = imd_obj.xmlid_to_res_id('account.invoice_form')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [(form_view_id, 'form')],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
            'res_id': invoice.id,
        }
