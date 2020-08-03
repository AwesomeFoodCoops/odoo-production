# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Column Section
    is_capital_fundraising = fields.Boolean(
        string='Concerns Capital Fundraising')

    fundraising_category_id = fields.Many2one(
        comodel_name='capital.fundraising.category',
        string='Fundraising Category')

    # Overload Section
    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None, date=None, description=None,
            journal_id=None):
        journal = self.env['account.journal'].browse(journal_id)
        # Get journal refund from category fundraising
        journal_refund_ids =\
            invoice.fundraising_category_id.journal_refund_ids.ids
        if not journal.is_capital_refund_fundraising and journal_refund_ids:
            # Get first journal refund
            journal_id = journal_refund_ids[0]
        res = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        res['is_capital_fundraising'] = invoice.is_capital_fundraising
        res['fundraising_category_id'] = invoice.fundraising_category_id.id
        # Set Account from fundraising category
        if invoice.fundraising_category_id:
            for line in res['invoice_line_ids']:
                line[2]['account_id'] = \
                    invoice.fundraising_category_id.capital_account_id.id
        # Set saleman is curent user
        res['user_id'] = invoice.env.user.id
        if res['date_due'] and res['date_due'] < date_invoice:
            res['date_due'] = date_invoice
        return res

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        invoice_id = move_lines[0][2]['invoice_id']
        if self.browse(invoice_id).is_capital_fundraising:
            for i in range(len(move_lines)):
                product_id = move_lines[i][2]['product_id']
                if product_id:
                    break
            if product_id:
                for i in range(len(move_lines)):
                    move_lines[i][2]['product_id'] = product_id
        return move_lines

    # Constraint Section
    @api.multi
    @api.constrains(
        'is_capital_fundraising', 'fundraising_category_id',
        'partner_id', 'invoice_line_ids', 'state')
    def _check_capital_fundraising(self):
        self.ensure_one()
        invoice = self
        product_ids = invoice.invoice_line_ids.mapped('product_id.id')

        if invoice.is_capital_fundraising:
            # Check mandatory field
            if not invoice.fundraising_category_id:
                raise exceptions.UserError(_(
                    "A Capital fundraising must have a capital category"
                    " defined"))

            # Check products
            forbidden_product_ids =\
                list(set(product_ids) - set(
                    [invoice.fundraising_category_id.product_id.id]))
            if forbidden_product_ids:
                forbidden_products = self.env['product.product'].browse(
                    forbidden_product_ids)
                if not all(
                    [each_prod.is_deficit_product
                     for each_prod in forbidden_products]):
                    raise exceptions.UserError(_(
                        "%s category do not allow %s products") % (
                        invoice.fundraising_category_id.name, ', '.join(
                            forbidden_products.mapped('name'))))

#            ordered_qty = sum(invoice.invoice_line_ids.mapped('quantity'))

#            to_order_qty = invoice.fundraising_category_id.check_minimum_qty(
#                invoice.partner_id)

#            if ordered_qty < to_order_qty:
#                raise exceptions.UserError(_(
#                    "This category and (previous orders) requires at least"
#                    " %d shares.") % (to_order_qty))
        else:
            capital_product_ids = self.env['product.product'].search(
                [('is_capital_fundraising', '=', True)]).ids
            forbidden_product_ids =\
                list(set(product_ids).intersection(capital_product_ids))
            if forbidden_product_ids:
                forbidden_product_names = ', '.join(
                    self.env['product.product'].browse(
                        forbidden_product_ids).mapped('name'))
                raise exceptions.UserError(_(
                    "Non capital invoice do not accept line with capital"
                    " subscription products : %s") % (forbidden_product_names))

        if invoice.state in ['open', 'paid']\
                and invoice.fundraising_category_id:

            category = invoice.fundraising_category_id
            # Get default minimum qty
            minimum_qty = category.minimum_share_qty

            # Compute minimum qty depending of partner state
            if invoice.partner_id.fundraising_partner_type_ids:
                for line in category.line_ids:
                    if (
                        line.fundraising_partner_type_id.id in
                        invoice.partner_id.fundraising_partner_type_ids.ids
                    ):
                        minimum_qty = min(line.minimum_share_qty, minimum_qty)

            capital_qty = 0
            category_invoices = self.search([
                ('partner_id', '=', invoice.partner_id.id),
                ('state', 'in', ['open', 'paid']),
                ('fundraising_category_id', '=', category.id)])
            for category_invoice in category_invoices:
                if category_invoice.type == 'out_invoice':
                    capital_qty += sum(
                        [inv_line.quantity
                         for inv_line in category_invoice.invoice_line_ids
                         if inv_line.product_id and
                         inv_line.product_id.is_capital_fundraising])
                else:
                    capital_qty -= sum(
                        [inv_line.quantity
                         for inv_line in category_invoice.invoice_line_ids
                         if inv_line.product_id and
                         inv_line.product_id.is_capital_fundraising])
            if capital_qty < 0:
                raise exceptions.UserError(_(
                    "You try to make an operation after which the partner"
                    " will have %d shares of capital of kind '%s'.\n\n"
                    " Incorrect Value.") % (capital_qty, category.name))
            if capital_qty < minimum_qty and capital_qty != 0 and\
                    not self.env.context.get(
                        'ignore_type_A_constrains', False):
                # use this test to ignore type A constrains when
                # partial transfer capital will be implemented. IE :
                # Partner bought 10 shares
                # Partner gives 5 shares to another member (*)
                # (5 shares left)
                # Partner ask refund for the other shares (0 shares left)
                # (*) : this invoice confirmation should be accepted,
                # even if the partner has 5 shares during this step.
                raise exceptions.UserError(_(
                    "You try to make an operation after which the partner"
                    " will have %d share(s) of capital of kind '%s'.\n\n"
                    " Minimum quantity : %d.") % (
                        capital_qty, category.name, minimum_qty))

    # OnChange Section
    @api.onchange('fundraising_category_id')
    def onchange_fundraising_category_id(self):
        if self.fundraising_category_id:
            self.journal_id = \
                self.fundraising_category_id.fundraising_id.journal_id
            if self.fundraising_category_id.partner_account_id:
                self.account_id =\
                    self.fundraising_category_id.partner_account_id

    @api.multi
    def apply_refund_deficit_share(self, quantity=0):
        '''
        @Function to apply the deficit share on customer refund
        '''

        for invoice in self:
            fundraising_categ = invoice.fundraising_category_id
            if invoice.type == 'out_refund' and fundraising_categ \
               and quantity >= 0:
                # Change the customer account of the refund
                if fundraising_categ.refund_account_id:
                    invoice.account_id = fundraising_categ.refund_account_id.id
                deficit_share_amount = \
                    fundraising_categ.get_deficit_share_amount(
                        invoice.date_invoice)

                for inv_line in invoice.invoice_line_ids:
                    source_product = inv_line.product_id
                    if source_product and \
                            source_product.is_capital_fundraising:
                        if not source_product.deficit_share_account_id and \
                                deficit_share_amount:
                            raise UserError(_("Deficit Share Account has not "
                                              "been configured for %s.") %
                                            source_product.display_name)
                        # Update quantity of source product line
                        inv_line.write({'quantity': quantity})

                        if deficit_share_amount:
                            # Adjust the Unit Price of the line
                            deficit_price_unit_signed = \
                                -1.0 * deficit_share_amount

                            if fundraising_categ.capital_account_id:
                                inv_line.account_id = \
                                    fundraising_categ.capital_account_id.id

                            # Create a new line
                            deficit_share_prod = \
                                fundraising_categ.deficit_product_id

                            deficit_line_val = {
                                'product_id':
                                    deficit_share_prod and
                                    deficit_share_prod.id or
                                    False,
                                'name': deficit_share_prod and
                                    deficit_share_prod.display_name or
                                    _('Deficit Share'),
                                'account_id':
                                    source_product.deficit_share_account_id.id,
                                'quantity': quantity,
                                'price_unit': deficit_price_unit_signed,
                                'uom_id':
                                    inv_line.uom_id and inv_line.uom_id.id or
                                    False,
                                'invoice_id': invoice.id
                            }

                            self.env['account.invoice.line'].create(
                                deficit_line_val)

                            # break because the quantity is total shares
                            # and we don't have different capital fundraising
                            # products in one invoice, therefore break when
                            # we get the first one satisfy and update with
                            # total quantity.
                            break

    @api.multi
    def register_payment(
        self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False
    ):
        res = super().register_payment(
            payment_line, writeoff_acc_id, writeoff_journal_id)
        # Generate capital
        if payment_line.full_reconcile_id:
            payment_line.full_reconcile_id.generate_capital_entrie(undo=False)
        return res
