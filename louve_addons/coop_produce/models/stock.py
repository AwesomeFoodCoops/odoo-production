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


from datetime import date, datetime
from dateutil import relativedelta
import json
import time
import sets

import openerp
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api, models
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging
_logger = logging.getLogger(__name__)


class StockInventory(osv.osv):
	_inherit = "stock.inventory"

	def action_add(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_add   -------------------')
		return True

	def action_reinitialiser(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_reinitialiser   -------------------')
		return True

	def _get_number_week(self, cr, uid, ids, date, args, context=None):
		_logger.info('------------------  _get_number_week   -------------------')
		week_number = 1
        	for data in self.browse(cr, uid, ids, context=context):
			if date :
				week_number = data.date.isocalendar()
        	return week_number

	_columns = {

		#'week_number': fields.function(_get_number_week, type="integer",string= "N° Semaine", help="Number of Inventory Week"),
		'week_number': fields.integer(string= "N° Semaine", help="Number of Inventory Week"),
		'hide_initialisation': fields.boolean(string="Cacher Intialisation",help="Cacher Initialisation"),
        	'categ_ids': fields.many2many('product.category', 'stock_inventory_product_categ', 'inventory_id', 'categ_id', 'Product Categories'),
		'supplier_ids': fields.many2many('res.partner', 'stock_inventory_res_partner', 'inventory_id', 'supplier_id', 'Supplier', help="Specify Product Category to focus in your inventory."),

	}

	_defaults = {
        	'name': 'Inventaire des F&L de la semaine',
	}

	def action_generate_planification(self, cr, uid, ids, context=None):
		""" Generate the Planification
		"""
        	return True

class StockInventoryLine(osv.osv):
	_inherit = "stock.inventory.line"

	def _get_theoretical_qty_ref(self, cr, uid, ids,name, args, context=None):
		_logger.info('------------------  _get_qty_details   -------------------')
		res = {}
        	for product in self.browse(cr, uid, ids, context=context):
			if product.product_id.product_tmpl_id.colissage_ref != 0 :
				res[product.id] = product.theoretical_qty / product.product_id.product_tmpl_id.colissage_ref
        	return res

	def _get_qty_stock(self, cr, uid, ids,name, args, context=None):
		_logger.info('------------------  _get_qty_loss   -------------------')
		res = {}
        	for product in self.browse(cr, uid, ids, context=context):
			if product.product_id.product_tmpl_id.colissage_ref != 0 :
				res[product.id] = product.product_qty / product.product_id.product_tmpl_id.colissage_ref
        	return res

	def _get_qty_loss(self, cr, uid, ids,name, args, context=None):
		_logger.info('------------------  _get_qty_stock   -------------------')
		res = {}
		theoretical_qty_ref = 0
		qty_stock = 0
        	for product in self.browse(cr, uid, ids, context=context):
			theoretical_qty_ref = product.theoretical_qty_ref
			qty_stock = product.qty_stock
			res[product.id] = theoretical_qty_ref - qty_stock
        	return res

	_columns = {
		'colisage_ref': fields.related('product_id', 'colissage_ref', type='float', relation='product.template', string='Colisage Ref', store=True, select=True, readonly=True),
		'theoretical_qty_ref': fields.function(_get_theoretical_qty_ref, type="float",digits_compute=dp.get_precision('Product Unit of Measure'),string='Theoretical Quantity',help="Quantity Theoric Of Reference"),
		'qty_loss': fields.function(_get_qty_loss, type="float",string='Quantity Lost', digits_compute=dp.get_precision('Product Unit of Measure'),help='Quantity Theoric Of Reference - Stock Quantity'),
		'qty_stock': fields.function(_get_qty_stock, type="float",string='Stock Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),help="Stock Quantity"),
	}

	def _default_stock_location(self, cr, uid, context=None):
		try:
		    warehouse = self.pool.get('ir.model.data').get_object(cr, uid, 'stock', 'warehouse0')
		    return warehouse.lot_stock_id.id
		except:
		    return False
	_defaults = {
        	'location_id': _default_stock_location,
	}
