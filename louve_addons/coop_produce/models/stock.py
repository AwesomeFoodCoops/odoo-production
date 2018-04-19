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


import sys
reload(sys)
sys.setdefaultencoding('utf8')

import logging
_logger = logging.getLogger(__name__)


class StockInventory(osv.osv):
	_inherit = "stock.inventory"

	def action_add_category(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_add_category   -------------------')
		value = {}
    		line_ids = []
		product_ids_list = []
        	for categ in self.browse(cr, uid, ids, context=context):
			if categ.line_ids : 
				categ.line_ids.unlink() 
			if categ.categ_ids : 
				if categ.supplier_ids : 
					product_supplier_ids = self.pool.get('product.supplierinfo').search(cr, uid,[('name','in',categ.supplier_ids.ids)])
					if product_supplier_ids :		
						for sup in product_supplier_ids :
							product_suppliers_ids = self.pool.get('product.supplierinfo').browse(cr, uid, sup, context=context).product_tmpl_id
							if categ.categ_ids :
								product_tmpl_ids = self.pool.get('product.template').search(cr, uid,[('id','in',product_suppliers_ids.ids),('categ_id','in',categ.categ_ids.ids)])
								if product_tmpl_ids :
									product_ids = self.pool.get('product.product').search(cr, uid,[('product_tmpl_id','in',product_tmpl_ids)])
									if product_ids : 
										for product in product_ids :
											line_ids.append((0,0, {'product_id':product,'qty_stock':0}))
										categ.write({'line_ids': line_ids})

				else :
					product_tmpl_ids = self.pool.get('product.template').search(cr, uid,[('categ_id','in',categ.categ_ids.ids)])
					if product_tmpl_ids :
						product_ids = self.pool.get('product.product').search(cr, uid,[('product_tmpl_id','in',product_tmpl_ids)])
						if product_ids : 
							for product in product_ids :
								line_ids.append((0,0, {'product_id':product,'qty_stock':0}))
							categ.write({'line_ids': line_ids})


	def action_add_supplier(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_add_supplier   -------------------')
    		line_ids = []
		product_ids_list = []
        	for supplier in self.browse(cr, uid, ids, context=context):
			if supplier.line_ids : 
				supplier.line_ids.unlink() 
			if supplier.supplier_ids : 
				product_supplier_ids = self.pool.get('product.supplierinfo').search(cr, uid,[('name','in',supplier.supplier_ids.ids)])
				if product_supplier_ids :		
					for sup in product_supplier_ids :
						product_suppliers_ids = self.pool.get('product.supplierinfo').browse(cr, uid, sup, context=context).product_tmpl_id
						if supplier.categ_ids :
							product_tmpl_ids = self.pool.get('product.template').search(cr, uid,[('id','in',product_suppliers_ids.ids),('categ_id','in',supplier.categ_ids.ids)])
							if product_tmpl_ids :
								product_ids = self.pool.get('product.product').search(cr, uid,[('product_tmpl_id','in',product_tmpl_ids)])
								if product_ids : 
									for product in product_ids :
										line_ids.append((0,0, {'product_id':product,'qty_stock':0}))
									supplier.write({'line_ids': line_ids})

						else :
							product_ids = self.pool.get('product.product').search(cr, uid,[('product_tmpl_id','in',product_suppliers_ids.ids)])
							if product_ids : 
								for product in product_ids :
									line_ids.append((0,0, {'product_id':product,'qty_stock':0}))
								supplier.write({'line_ids': line_ids})


	def action_reinitialise(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_reinitialise   -------------------')
        	for line in self.browse(cr, uid, ids, context=context):
			if line.categ_ids : 
				for categ in line.categ_ids :
					line.write({'categ_ids': [( 3, categ.id)]}) 
			if line.supplier_ids : 
				for supplier in line.supplier_ids :
					line.write({'supplier_ids': [( 3, supplier.id)]}) 
			if line.line_ids : 
				line.line_ids.unlink() 


	def _get_number_week(self, cr, uid, ids, date, args, context=None):
		_logger.info('------------------  _get_number_week   -------------------')
		res = {}
		week_number = 1
        	for data in self.browse(cr, uid, ids, context=context):
			date = datetime.datetime.strptime(data.date, "%Y-%m-%d %H:%M:%S")
			week_number = date.isocalendar()[1]
			res[data.id] = week_number
        	return res

	_columns = {

		'week_number': fields.function(_get_number_week, type="integer",string= "N° Semaine", help="Number of Inventory Week", store=True),
		'hide_initialisation': fields.boolean(string="Cacher Intialisation",help="Cacher Initialisation"),
        	'categ_ids': fields.many2many('product.category', 'stock_inventory_product_categ', 'inventory_id', 'categ_id', 'Product Categories'),
		'supplier_ids': fields.many2many('res.partner', 'stock_inventory_res_partner', 'inventory_id', 'supplier_id', 'Supplier', domain=[('supplier', '=', True)],help="Specify Product Category to focus in your inventory."),
		'weekly_inventory': fields.boolean(string="Inventaire Hebdomadaire",help="Inventaire Hebdomadaire"),
	}

	_defaults = {
        	'name': 'Inventaire des F&L de la Semaine',
	}

	def action_generate_planification(self, cr, uid, ids, context=None):
		""" Generate the Planification
		"""

                week_date = False
                week_number = False
		product_ids_list = []
                for order in self.browse(cr, uid, ids, context=context) :
                        week_date = order.date
                        week_number = order.week_number
			for product in order.line_ids:
				product_ids_list.append(product.product_id.id)
			planification_ids = self.pool('stock.inventory').search(cr, uid, [('week_number','=',week_number)], context=context)
			if planification_ids :
				for planif in planification_ids :
					line_ids =  self.pool('stock.inventory').browse(cr, uid, planif, context=context).line_ids
					for product in line_ids:
						if product.product_id.id in product_ids_list :
							product_name = product.product_id.name_template
							raise osv.except_osv(('Error'), ("Une planification est déjà en cours pour le : " + product_name))
		        				return False
						else : 
							view_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','order.week.planning'),('name','=','order.week.planning.form')], context=context)
							return {
									    'name': "Planfication Des Commandes",
									    'view_type': 'form',
									    'res_model': 'order.week.planning',
									    'view_id': view_id[0],
									    'view_mode': 'form',
									    'nodestroy': True,
									    'target': 'current',
									    'context': {'default_date': week_date,'default_week_number': week_number},
									    'flags': {'form': {'action_buttons': False}},
									    'type': 'ir.actions.act_window',
							}
			else :
				view_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','order.week.planning'),('name','=','order.week.planning.form')], context=context)
		                return {
		                            'name': "Planfication Des Commandes",
		                            'view_type': 'form',
		                            'res_model': 'order.week.planning',
		                            'view_id': view_id[0],
		                            'view_mode': 'form',
		                            'nodestroy': True,
		                            'target': 'current',
		                            'context': {'default_date': week_date,'default_week_number': week_number},
		                            'flags': {'form': {'action_buttons': False}},
		                            'type': 'ir.actions.act_window',
		                }

class StockInventoryLine(osv.osv):
	_inherit = "stock.inventory.line"

	def _get_theoretical_qty_ref(self, cr, uid, ids,name, args, context=None):
		_logger.info('------------------  _get_qty_details   -------------------')
		res = {}
        	for product in self.browse(cr, uid, ids, context=context):
			theoretical_qty = 0.0
			if product.product_id.product_tmpl_id.colissage_ref != 0 :
				theoretical_qty = product.theoretical_qty / product.product_id.product_tmpl_id.colissage_ref
			res[product.id] = theoretical_qty
        	return res


	def _get_qty_loss(self, cr, uid, ids,name, args, context=None):
		_logger.info('------------------  _get_qty_loss   -------------------')
		res = {}
		theoretical_qty_ref = 0
		qty_stock = 0
        	for product in self.browse(cr, uid, ids, context=context):
			theoretical_qty_ref = product.theoretical_qty_ref
			qty_stock = product.qty_stock
			res[product.id] = theoretical_qty_ref - qty_stock
        	return res

	def _get_product_category(self, cr, uid, ids,name, args, context=None):
		_logger.info('------------------  _get_product_category   -------------------')
		res = {}
		product_category = False
        	for product in self.browse(cr, uid, ids, context=context):
			_logger.info(product)
			product_category = product.product_id.product_tmpl_id.categ_id.id
			res[product.id] = product_category
        	return res


	_columns = {

		'colisage_ref': fields.related('product_id', 'colissage_ref', type='float', relation='product.template', string='Colisage Ref', store=True, select=True, readonly=True),
		'theoretical_qty_ref': fields.function(_get_theoretical_qty_ref, type="float",digits_compute=dp.get_precision('Product Unit of Measure'),string='Theoretical Quantity',help="Quantity Theoric Of Reference"),
		'qty_loss': fields.function(_get_qty_loss, type="float",string='Quantity Lost', digits_compute=dp.get_precision('Product Unit of Measure'),help='Quantity Theoric Of Reference - Stock Quantity'),
		'qty_stock': fields.float(string='Stock Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),help="Stock Quantity"),
		'categ_id': fields.function(_get_product_category, type="integer", string='Category Product', store=True, help="Category Product"),

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


	@api.onchange('qty_stock')
	def onchange_qty_stock(self):
		_logger.info('----------------- onchange_qty_stock  -----------------')
		product_qty = 0
		for record in self : 
			if record.qty_stock:
				product_qty = record.qty_stock / record.product_id.product_tmpl_id.colissage_ref
				record.product_qty = product_qty


class OrderWeekPlanning(osv.osv):
	_name = "order.week.planning"
	_description = "Order Week Planning"

	def action_close_week(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_close_week   -------------------')
		return True

	def action_reception_week(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_reception_week   -------------------')
                week_number = False
                for order in self.browse(cr, uid, ids, context=context) :
			_logger.info('------------------  order   -------------------')
			_logger.info(order)
			if order.line_ids:
				for supplier in order.line_ids :
					order_ids = self.pool['stock.picking'].search(cr, uid, [('partner_id','in',supplier.partner_id.ids)], context=context)
					if order_ids :
						view_form_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','stock.picking'),('name','=','stock.picking.form')], context=context)
						view_tree_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','stock.picking'),('name','=','stock.picking.tree')], context=context)
						view_kanban_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','stock.picking'),('name','=','stock.picking.kanban')], context=context)
						return {
									    'name': "Réceptions De La Semaine",
									    'view_type': 'form',
									    'view_mode': 'kanban,tree,form',
									    'res_model': 'stock.picking',
									    'views': [(view_kanban_id[0], 'kanban'),(view_tree_id[0], 'tree'),(view_form_id[0], 'form')],    
									    'nodestroy': True,
									    'target': 'current',
							   		    'domain': [],
									    'flags': {'form': {'action_buttons': False}},
									    'type': 'ir.actions.act_window',
						}
					else : 
						raise osv.except_osv(('Error'), ("Aucune Réception Enregistrée"))
						return False
			else :
				raise osv.except_osv(('Error'), ("Aucun Produit Enregistré"))
				return False

	def action_commande_week(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_commande_week   -------------------')
                week_number = False
                for order in self.browse(cr, uid, ids, context=context) :
                        week_date = order.date
			order_ids = self.pool['sale.order'].search(cr, uid, [], context=context)
			view_form_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','sale.order'),('name','=','sale.order.form')], context=context)
			view_tree_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','sale.order'),('name','=','sale.order.tree')], context=context)
			return {
				                    'name': "Liste Des Commandes",
						    'view_type': 'form',
						    'view_mode': 'tree,form',
				                    'res_model': 'sale.order',
						    'views': [(view_tree_id[0], 'tree'),(view_form_id[0], 'form')],    
				                    'nodestroy': True,
				                    'target': 'current',
				   		    'domain': [],
				                    'flags': {'form': {'action_buttons': False}},
				                    'type': 'ir.actions.act_window',
			}


	def action_other_weeks(self, cr, uid, ids, context=None):
		_logger.info('------------------ action_other_weeks   -------------------')
                week_id = False
                for order in self.browse(cr, uid, ids, context=context) :
                        week_id = order.id
			view_form_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','stock.inventory'),('name','=','stock.inventory.form')], context=context)
			view_tree_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','stock.inventory'),('name','=','stock.inventory.tree')], context=context)
			return {
				                    'name': "Voir Les Autres Semaines",
						    'view_type': 'form',
						    'view_mode': 'tree,form',
				                    'res_model': 'stock.inventory',
						    'views': [(view_tree_id[0], 'tree'),(view_form_id[0], 'form')],    
				                    'nodestroy': True,
				                    'target': 'current',
				   		    'domain': [('id', '!=', week_id)],
				                    'flags': {'form': {'action_buttons': False}},
				                    'type': 'ir.actions.act_window',
			}


	def action_add_category(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_add_category   -------------------')
		value = {}
    		line_ids = []
		product_ids_list = []
        	for categ in self.browse(cr, uid, ids, context=context):
			if categ.line_ids : 
				categ.line_ids.unlink() 
			if categ.categ_ids : 
				if categ.supplier_ids : 
					product_supplier_ids = self.pool.get('product.supplierinfo').search(cr, uid,[('name','in',categ.supplier_ids.ids)])
					if product_supplier_ids :		
						for sup in product_supplier_ids :
							product_suppliers_ids = self.pool.get('product.supplierinfo').browse(cr, uid, sup, context=context).product_tmpl_id
							if categ.categ_ids :
								product_tmpl_ids = self.pool.get('product.template').search(cr, uid,[('id','in',product_suppliers_ids.ids),('categ_id','in',categ.categ_ids.ids)])
								if product_tmpl_ids :
									product_ids = self.pool.get('product.product').search(cr, uid,[('product_tmpl_id','in',product_tmpl_ids)])
									if product_ids : 
										for product in product_ids :
											line_ids.append((0,0, {'product_id':product,'qty_stock':0}))
										categ.write({'line_ids': line_ids})

				else :
					product_tmpl_ids = self.pool.get('product.template').search(cr, uid,[('categ_id','in',categ.categ_ids.ids)])
					if product_tmpl_ids :
						product_ids = self.pool.get('product.product').search(cr, uid,[('product_tmpl_id','in',product_tmpl_ids)])
						if product_ids : 
							for product in product_ids :
								line_ids.append((0,0, {'product_id':product,'qty_stock':0}))
							categ.write({'line_ids': line_ids})


	def action_add_supplier(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_add_supplier   -------------------')
    		line_ids = []
		product_ids_list = []
        	for supplier in self.browse(cr, uid, ids, context=context):
			if supplier.line_ids : 
				supplier.line_ids.unlink() 
			if supplier.supplier_ids : 
				product_supplier_ids = self.pool.get('product.supplierinfo').search(cr, uid,[('name','in',supplier.supplier_ids.ids)])
				if product_supplier_ids :		
					for sup in product_supplier_ids :
						product_suppliers_ids = self.pool.get('product.supplierinfo').browse(cr, uid, sup, context=context).product_tmpl_id
						if supplier.categ_ids :
							product_tmpl_ids = self.pool.get('product.template').search(cr, uid,[('id','in',product_suppliers_ids.ids),('categ_id','in',supplier.categ_ids.ids)])
							if product_tmpl_ids :
								product_ids = self.pool.get('product.product').search(cr, uid,[('product_tmpl_id','in',product_tmpl_ids)])
								if product_ids : 
									for product in product_ids :
										line_ids.append((0,0, {'product_id':product,'qty_stock':0}))
									supplier.write({'line_ids': line_ids})

						else :
							product_ids = self.pool.get('product.product').search(cr, uid,[('product_tmpl_id','in',product_suppliers_ids.ids)])
							if product_ids : 
								for product in product_ids :
									line_ids.append((0,0, {'product_id':product,'qty_stock':0}))
								supplier.write({'line_ids': line_ids})


	def action_reinitialise(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_reinitialise   -------------------')
        	for line in self.browse(cr, uid, ids, context=context):
			if line.categ_ids : 
				for categ in line.categ_ids :
					line.write({'categ_ids': [( 3, categ.id)]}) 
			if line.supplier_ids : 
				for supplier in line.supplier_ids :
					line.write({'supplier_ids': [( 3, supplier.id)]}) 
			if line.line_ids : 
				line.line_ids.unlink() 


	def action_update(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_update   -------------------')
		return True


	_columns = {
        	'week_number': fields.integer(string= "N° Semaine", required=True, help="The date that will be used for the stock level check of the products and the validation of the stock move related to this inventory."),
        	'date': fields.datetime('Semaine', required=True, help="The date that will be used for the stock level check of the products and the validation of the stock move related to this inventory."),
        	'week_date': fields.datetime(string= "Date", required=True, help="The date that will be used for the stock level check of the products and the validation of the stock move related to this inventory."),		
		'hide_initialisation': fields.boolean(string="Cacher Intialisation",help="Cacher Initialisation"),
        	'categ_ids': fields.many2many('product.category', 'stock_inventory_product_categ', 'inventory_id', 'categ_id', 'Product Categories'),
		'supplier_ids': fields.many2many('res.partner', 'stock_inventory_res_partner', 'inventory_id', 'supplier_id', 'Supplier', help="Specify Product Category to focus in your inventory."),
		
        	'line_ids': fields.one2many('order.week.planning.line', 'order_id', 'Orders', help="Order Lines."),

		'total_command_monday': fields.float('Total Commands Monday', digits_compute=dp.get_precision('Product Unit of Measure')),
		'total_command_tuesday': fields.float('Total Commands Tuesday', digits_compute=dp.get_precision('Product Unit of Measure')),		
		'total_command_wednesday': fields.float('Total Commands Wednesday', digits_compute=dp.get_precision('Product Unit of Measure')),		
		'total_command_thirsday': fields.float('Total Commands Thirsday', digits_compute=dp.get_precision('Product Unit of Measure')),		
		'total_command_friday': fields.float('Total Commands Friday', digits_compute=dp.get_precision('Product Unit of Measure')),		
		'total_command_saturday': fields.float('Total Commands Saturday', digits_compute=dp.get_precision('Product Unit of Measure')),	
		'total_command_sunday': fields.float('Total Commands Saturday', digits_compute=dp.get_precision('Product Unit of Measure')),

		'total_received_monday': fields.float('Total Recu Monday', digits_compute=dp.get_precision('Product Unit of Measure')),
		'total_received_tuesday': fields.float('Total Recu Tuesday', digits_compute=dp.get_precision('Product Unit of Measure')),		
		'total_received_wednesday': fields.float('Total Recu Wednesday', digits_compute=dp.get_precision('Product Unit of Measure')),		
		'total_received_thirsday': fields.float('Total Recu Thirsday', digits_compute=dp.get_precision('Product Unit of Measure')),		
		'total_received_friday': fields.float('Total Recu Friday', digits_compute=dp.get_precision('Product Unit of Measure')),		
		'total_received_saturday': fields.float('Total Recu Saturday', digits_compute=dp.get_precision('Product Unit of Measure')),	
		'total_received_sunday': fields.float('Total Recu Saturday', digits_compute=dp.get_precision('Product Unit of Measure')),							
	}




class OrderWeekPlanningLine(osv.osv):
	_name = "order.week.planning.line"
	_description = "Order Week Planning Line"

	def action_edit_price(self, cr, uid, ids, context=None):
		_logger.info('------------------  action_edit_price   -------------------')
        	for price in self.browse(cr, uid, ids, context=context):
			price.write({'edit_price':True})


	_columns = {
		'order_id': fields.many2one('order.week.planning', 'Order Week', ondelete='cascade', select=True),
		'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
		'colisage_ref': fields.related('product_id', 'colissage_ref', type='float', relation='product.template', string='Colisage Ref', store=True, select=True, readonly=True),
		'partner_id': fields.many2one('res.partner', 'Suupplier'),		
		'list_price': fields.related('product_id', 'list_price', type='float', relation='product.template', string='List Price', store=True, select=True),

		'vendu-s-2': fields.float('Vendu S-2', digits_compute=dp.get_precision('Product Unit of Measure')),
		'vendu-s-1': fields.float('Vendu S-1', digits_compute=dp.get_precision('Product Unit of Measure')),
		'vendu-s-inv': fields.float('Vendu S INV', digits_compute=dp.get_precision('Product Unit of Measure')),

		'monday_line': fields.float('L', digits_compute=dp.get_precision('Product Unit of Measure')),
		'tuesday_line': fields.float('M', digits_compute=dp.get_precision('Product Unit of Measure')),
		'wednesday_line': fields.float('M', digits_compute=dp.get_precision('Product Unit of Measure')),

		'inv_int': fields.float('Inv Int', digits_compute=dp.get_precision('Product Unit of Measure')),

		'thirsday_line': fields.float('J', digits_compute=dp.get_precision('Product Unit of Measure')),
		'friday_line': fields.float('V', digits_compute=dp.get_precision('Product Unit of Measure')),
		'saturday_line': fields.float('S', digits_compute=dp.get_precision('Product Unit of Measure')),

		'total_in': fields.float('Total + S Inv', digits_compute=dp.get_precision('Product Unit of Measure')),
		'e_in': fields.float('E Inv', digits_compute=dp.get_precision('Product Unit of Measure')),

		'loss': fields.float('Perte', digits_compute=dp.get_precision('Product Unit of Measure')),
		'sold': fields.float('Vendu', digits_compute=dp.get_precision('Product Unit of Measure')),
		'edit_price': fields.boolean(string="Editer Prix",help="Editer Prix", default=False),
	}


	def action_view_history(self, cr, uid, ids, context=None):
		""" View History Product
		"""

                product_id = False
                colissage_ref = False
                for product in self.browse(cr, uid, ids, context=context) :
                        product_id= product.product_id.id
                        colissage_ref = product.colisage_ref
			view_id = self.pool['ir.ui.view'].search(cr, uid, [('model','=','planification.product.history'),('name','=','coop.product.product.history.form')], context=context)
                        return {
                                    'name': "Historique Du Produit",
                                    'view_type': 'form',
                                    'res_model': 'planification.product.history',
                                    'view_id': view_id[0],
                                    'view_mode': 'form',
                                    'nodestroy': True,
                                    'target': 'current',
                                    'context': {'default_product_id': product_id,'default_colissage_ref': colissage_ref},
                                    'flags': {'form': {'action_buttons': False}},
                                    'type': 'ir.actions.act_window',
                        }

class PlanificationHistoriqueProduit(osv.osv):
	_name = "planification.product.history"


	_description = "Product History"


	_columns = {

		'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
		'colissage_ref': fields.float('Total Commands Monday', digits_compute=dp.get_precision('Product Unit of Measure')),
        	'line_ids': fields.one2many('planification.product.history.line', 'history_id', 'Historique', help="Historique Lines."),
	}



class PlanificationHistoriqueProduitLine(osv.osv):
	_name = "planification.product.history.line"
	_description = "Product History Line"


	_columns = {
		'history_id': fields.many2one('planification.product.history', 'Product History', ondelete='cascade', select=True),
		'semaine_nbre': fields.integer('N° Semaine', required=True, select=True),
		'prix_unitaire': fields.float('Prix Unitaire', digits_compute=dp.get_precision('Product Unit of Measure')),
		's_inv': fields.float('S Inv', digits_compute=dp.get_precision('Product Unit of Measure')),
		'monday_line': fields.float('L', digits_compute=dp.get_precision('Product Unit of Measure')),
		'tuesday_line': fields.float('M', digits_compute=dp.get_precision('Product Unit of Measure')),
		'wednesday_line': fields.float('M', digits_compute=dp.get_precision('Product Unit of Measure')),
		'inv_int': fields.float('Inv Int', digits_compute=dp.get_precision('Product Unit of Measure')),
		'thirsday_line': fields.float('J', digits_compute=dp.get_precision('Product Unit of Measure')),
		'friday_line': fields.float('V', digits_compute=dp.get_precision('Product Unit of Measure')),
		'saturday_line': fields.float('S', digits_compute=dp.get_precision('Product Unit of Measure')),
		'total_inv': fields.float('Total + S Inv', digits_compute=dp.get_precision('Product Unit of Measure')),
		'e_inv': fields.float('E Inv', digits_compute=dp.get_precision('Product Unit of Measure')),
		'loss': fields.float('Perte', digits_compute=dp.get_precision('Product Unit of Measure')),
		'sold': fields.float('Vendu', digits_compute=dp.get_precision('Product Unit of Measure')),
	}





