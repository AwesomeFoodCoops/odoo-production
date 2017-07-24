##############################################################################
#
#    POS Payment Terminal module for Odoo
#    Copyright (C) 2014 Aurélien DUMAINE
#    Copyright (C) 2015 Akretion (www.akretion.com)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
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
from odoo import api, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _payment_fields(self, ui_paymentline):
        result = super(PosOrder, self)._payment_fields(ui_paymentline)
        result['payment_terminal_return_message'] = ui_paymentline.get(
            'payment_terminal_return_message')
        return result

    def add_payment(self, data):
        self = self.with_context(
            dict(self.env.context,
                 **{'default_payment_terminal_return_message':
                        data.get('payment_terminal_return_message')})
        )
        return super(PosOrder, self).add_payment(data)
