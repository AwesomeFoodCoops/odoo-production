##############################################################################
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

from odoo import models, fields, api, _


class ComputedPurchaseOrderLine(models.Model):
    _inherit = 'computed.purchase.order.line'

    def get_psi(self, purchase_qty_package=None, operator='<=', order='min_nb_of_package DESC'):
        if purchase_qty_package is None:
            purchase_qty_package = self.purchase_qty_package
        args = [
            ('name', '=', self.computed_purchase_order_id.partner_id.id),
            "|",
            ("product_id", "=", self.product_id.id),
            ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
            ("min_nb_of_package", operator, purchase_qty_package),
        ]
        psi = self.env["product.supplierinfo"].sudo().search(args, order=order, limit=1)
        return psi
