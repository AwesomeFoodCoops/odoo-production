# -*- coding: utf-8 -*-
##############################################################################
#
#    POS Payment Terminal module for Odoo
#    Copyright (C) 2014 Aurélien DUMAINE
#    Copyright (C) 2015 Akretion (www.akretion.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_mode = fields.Selection(
        (('card', 'Card'), ('check', 'Check')), 'Payment mode',
        help="Select the payment mode sent to the payment terminal")


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_payment_terminal = fields.Boolean(
        'Payment Terminal',
        help="A payment terminal is available on the Proxy")

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _payment_fields(self, cr, uid, ui_paymentline, context=None):
        print ui_paymentline
        result = super(PosOrder, self).\
            _payment_fields(cr, uid, ui_paymentline, context=context)
        result['payment_terminal_return_message'] = ui_paymentline.get('payment_terminal_return_message')
        return result

    def add_payment(self, cr, uid, order_id, data, context=None):
        if context != None:
            new_context = context.copy()
        else :
            new_context = {} 
        new_context['default_payment_terminal_return_message'] = data.get('payment_terminal_return_message')
        return super(PosOrder, self).add_payment(cr, uid, order_id, data, new_context)


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    payment_terminal_return_message = fields.Char('payment terminal return message')
    remittance_number = fields.Char('Remittance number')
    transaction_number = fields.Char('Transaction number')
    card_number = fields.Char('Card number')
