# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import models, fields, api


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    @api.multi
    def reverse_moves(self):
        payment_id = self._context.get('payment_id', False)
        account_move_ids = self._context.get('active_ids', False)

        # Get move line to unreconcile automaticly
        account_moves = self.env['account.move'].browse(account_move_ids)
        lines_reconciled = account_moves.mapped('line_ids').filtered(
            lambda l: l.reconciled)
        if lines_reconciled:
            lines_reconciled.remove_move_reconcile()

        res = super(AccountMoveReversal, self).reverse_moves()

        # If exist payment, change state to cancelled
        payment = self.env['account.payment'].browse(payment_id)
        if payment:
            payment.state = 'cancelled'
            return {'type': 'ir.actions.act_window_close'}
        return res
