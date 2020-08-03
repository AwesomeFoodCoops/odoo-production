# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class AccountFullReconcile(models.Model):
    _inherit = 'account.full.reconcile'

    @api.multi
    def generate_capital_entrie(self, undo=False):
        move_obj = self.env['account.move']
        for reconcile in self:
            category_ids = reconcile.mapped(
                'reconciled_line_ids.invoice_id.fundraising_category_id')
            invoices = reconcile.mapped('reconciled_line_ids.invoice_id')
            # get payment entry
            payment_id = reconcile.mapped('reconciled_line_ids.payment_id')
            # get line to reconcile
            move_line = invoices.mapped('move_id.line_ids')
            line_to_reconcile = move_line.filtered(lambda l: l.credit != 0)
            # Do not create any extra entry for capital refund
            if not invoices or invoices[0].type == 'out_refund':
                continue

            if len(category_ids) > 1:
                raise UserError(_(
                    "You can not reconcile Capital Invoices for many"
                    " Categories: %s") % (
                        ', '.join(category_ids.mapped('name'))))
            elif len(category_ids) == 1 and category_ids[0].capital_account_id:
                # Create new account move
                category = category_ids[0]
                capital_entries_journal = (
                    category.fundraising_id.journal_ids
                    and category.fundraising_id.journal_ids
                    or category.fundraising_id.journal_id
                )
                partner = reconcile.reconciled_line_ids[0].partner_id

                move_lines = reconcile.mapped('reconciled_line_ids').filtered(
                    lambda r: r.journal_id.id in capital_entries_journal.ids)

                if not move_lines:
                    continue
                journal = move_lines[0].journal_id
                payment_move_lines = invoices[0].payment_move_line_ids

                payment_m_line = reconcile.mapped(
                    'reconciled_line_ids'
                ).filtered(
                    lambda ml: ml.id in payment_move_lines.ids
                )

                payment_date = (
                    payment_m_line
                    and payment_m_line[0].date
                    or fields.Date.context_today(self)
                )

                # Sale
                total = sum(move_lines.mapped('debit'))
                is_payment = not undo if total > 0 else undo

                lines_vals = [(0, 0, {
                    'name': _("Payment of Capital"),
                    'partner_id': partner.id,
                    'account_id':
                    category.product_id.property_account_income_id.id,
                    'product_id': category.product_id.id,
                    'invoice_id': invoices[0].id,
                    'debit': total if is_payment else 0,
                    'credit': 0 if is_payment else total,
                }), (0, 0, {
                    'name': _("Payment of Capital"),
                    'partner_id': partner.id,
                    'account_id': category.capital_account_id.id,
                    'product_id': category.product_id.id,
                    'invoice_id': invoices[0].id,
                    'debit': 0 if is_payment else total,
                    'credit': total if is_payment else 0,
                })]

                move_vals = {
                    'name': journal.sequence_id.next_by_id(),
                    'partner_id': partner.id,
                    'ref': ', '.join(invoices.mapped('number')),
                    'line_ids': lines_vals,
                    'journal_id': journal.id,
                    'date': payment_date,
                    'narration': _("Paid Capital"),
                }

                move = move_obj.create(move_vals)
                move.post()
                # add payment link
                # we do it after to avoid a constraint
                if payment_id:
                    move.mapped('line_ids').write({
                        'payment_id': payment_id[0].id,
                    })
                # auto reconcile
                if line_to_reconcile and not line_to_reconcile[0].reconciled:
                    reconcile.auto_reconcile_payment(
                        move, line_to_reconcile[0])

    @api.multi
    def auto_reconcile_payment(self, move, line_to_reconcile):
        # Auto reconcile when confirm payment

        self.ensure_one()
        line_reconcile = move.line_ids.filtered(
            lambda l: l.account_id.id == line_to_reconcile[0].account_id.id
            and not l.reconciled)
        line_to_reconcile |= line_reconcile

        line_to_reconcile.reconcile()
        return True
