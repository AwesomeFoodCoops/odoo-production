# -*- coding: utf-8 -*-

from openerp import api, models, fields, _


class account_payment(models.Model):
    _inherit = 'account.payment'

    account_move_ids = fields.One2many(
        'account.move', 'payment_id', 'Journals Entry')

    def _create_payment_entry(self, amount):
        move = super(account_payment, self)._create_payment_entry(amount)
        move.payment_id = self.id
        return move
