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
from openerp.exceptions import ValidationError
from openerp import models, fields, api, _

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.model
    def create(self, vals=None):
        if not vals.get('payment_terminal_return_message') and self._context.get('default_payment_terminal_return_message'):
            vals['payment_terminal_return_message'] = self._context['default_payment_terminal_return_message']
        if vals.get('payment_terminal_return_message'):
            if vals.get('remittance_number') or vals.get('transaction_number') or vals.get('card_number'):
                raise ValidationError(_('The value of remittance,transaction and card number must be null'))
            else:
                try:
                    if len(vals['payment_terminal_return_message']) == 80:
                        vals['card_number'] = vals['payment_terminal_return_message'][12:67]
                        priv = vals['payment_terminal_return_message'][70:80]
                    else:
                        priv = vals['payment_terminal_return_message'][15:25]
                    if priv[0] == '2':
                        vals['transaction_number'] = priv[1:4]
                        vals['remittance_number'] = priv[4:7]
                except Exception:
                    pass
        return super(AccountBankStatementLine, self).create(vals)
