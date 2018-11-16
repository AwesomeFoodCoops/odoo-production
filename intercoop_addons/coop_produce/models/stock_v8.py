# -*- coding: utf-8 -*-
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

import datetime
from openerp import SUPERUSER_ID, api, models, fields, _
import openerp.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)

class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.one
    @api.depends('date')
    def _get_week_number(self):
        if not self.date:
            self.week_number = 0
        else:
            week_number = datetime.datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S").strftime("%W")
            self.week_number = week_number

    week_number = fields.Integer(string="Week Number",
                                 compute="_get_week_number",
                                 store=True,
                                 help="Number of Inventory Week")


    @api.model
    def _get_planning_line_from_inv_line(self,inv_lines):
        line_vals = []
        for line in inv_lines:
            supplier_info = line.product_id.seller_ids and line.product_id.seller_ids[0] or False
            val = {
                'product_id':line.product_id.id,
                'supplier_id':supplier_info and supplier_info.name.id or False,
                'price_unit':supplier_info and supplier_info.base_price or 0.0, # set to this value because this value is used on purchase order
                'price_policy':supplier_info and supplier_info.price_policy or 0.0, # set to this value because this value is used on purchase order
                'default_packaging':line.product_id.default_packaging,
                'supplier_packaging':supplier_info and supplier_info.package_qty or 0,
                'start_inv':line.qty_stock # it should be this. To be vaildated by coop : line.packaging_qty * line.product_id.default_packaging/(supplier_info.package_qty or 1),
            }
            line_vals.append(val)
        return line_vals


    @api.multi
    def action_generate_planification(self):
        """ Generate the Planification
        """
        self.ensure_one()
        line_vals = self._get_planning_line_from_inv_line(self.line_ids)
        week_planning_obj = self.env['order.week.planning']

        week_planning_value = {
            'date':self.week_date,
            'line_ids':[(0,0,x) for x in line_vals],
            'hide_initialisation': True
        }
        new_id = week_planning_obj.create(week_planning_value)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'order.week.planning',
            'res_id': new_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.multi
    def action_done(self):
        for stock_inventory in self:
            if not stock_inventory.week_date:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.inventory.wizard',
                    'res_id': False,
                    'view_mode': 'form',
                    'target': 'new',
                }
        return super(StockInventory, self).action_done()
