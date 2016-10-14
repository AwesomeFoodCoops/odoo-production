# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from openerp import models, fields, api


class ComputedPurchaseOrderLine(models.Model):
    _inherit = 'computed.purchase.order.line'

    # Columns section
    displayed_product_history_ids = fields.Many2many(
        'displayed.product.history', related='product_id.product_history_ids',
        string='Product History')

    # Private section
    @api.multi
    def view_history(self):
        model, action_id = self.pool[
            'ir.model.data'].get_object_reference(
            self._cr, self._uid, 'product_history_for_cpo',
            "action_view_history")
        action = self.pool[model].read(
            self._cr, self._uid, action_id, context=self._context)
        ids = []
        history_ranges = []
        for cpol in self:
                ids.append(cpol.product_id.id)
                history_ranges.append(cpol.product_id.history_range)
        action['domain'] = [
            ('product_id', 'in', ids),
            ('history_range', 'in', history_ranges)]
        return action
