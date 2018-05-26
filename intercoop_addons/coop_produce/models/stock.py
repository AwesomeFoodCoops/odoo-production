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
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class StockInventory(osv.osv):
    _inherit = "stock.inventory"

    def _get_number_week(self, cr, uid, ids, date, args, context=None):
        _logger.info('------------------  _get_number_week   -------------------')
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            week_number = datetime.datetime.strptime(inv.date, "%Y-%m-%d %H:%M:%S").strftime("%W")
            res[inv.id] = week_number
        return res

    _columns = {
        'week_number': fields.integer(string="Week num.", readonly=True, help="Number of the week in the current year"),
        'week_date': fields.date(string="Began order schuduling on.", help="Week planning start date"),

        'hide_initialisation': fields.boolean(string="Hide initialisation area", help="Hide Init. area",
                                              states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'categ_ids': fields.many2many('product.category', 'stock_inventory_product_categ', 'inventory_id', 'categ_id',
                                      'Product categories',
                                      states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'supplier_ids': fields.many2many('res.partner', 'stock_inventory_res_partner', 'inventory_id', 'supplier_id',
                                         'Suppliers', domain=[('supplier', '=', True), ('is_company', '=', True)],
                                         help="Specify product category to focus in your inventory.",
                                         states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'weekly_inventory': fields.boolean(string="Is a weekly inventory",
                                           help="Technical field to distinct odoo inventory with weekkly inventory ",
                                           states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
    }


    def onchange_date(self, cr, uid, ids, date, context=None):
        res = {}
        if date:
            week_number = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%W")
            res['value'] = {'week_number': week_number}
        return res

    def _coop_produce_get_inventory_lines(self, cr, uid, inventory, context=None):
        '''
            Function inspired from stock/stock.py to add categories filters
            and adds categ_ids, suppliers to the filter
        '''
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        location_ids = location_obj.search(cr, uid, [('id', 'child_of', [inventory.location_id.id])], context=context)
        domain = ' sq.location_id in %s'
        product_ids = []
        vals = []
        args = (tuple(location_ids),)
        if inventory.company_id.id:
            domain += ' and sq.company_id = %s'
            args += (inventory.company_id.id,)

        # Look for already existing product
        already_added_product_ids = [line.product_id.id for line in inventory.line_ids]

        if inventory.categ_ids:
            domain += ' and product_id in %s'
            categ_ids = [x.id for x in inventory.categ_ids]

            # Look for products belong to selectec categories
            product_ids = product_obj.search(cr, uid, [('categ_id', 'in', categ_ids)], context=context)

        if inventory.supplier_ids:
            domain += ' and product_id in %s'
            supplier_ids = [x.id for x in inventory.supplier_ids]

            # Look for already existing product
            already_added_product_ids = [line.product_id.id for line in inventory.line_ids]

            # Look for products belong to selectec categories
            supplierinfo_ids = supplierinfo_obj.search(cr, uid, [('name', 'in', supplier_ids)], context=context)
            product_tmpls = supplierinfo_obj.read(cr, uid, supplierinfo_ids, ['product_tmpl_id'])
            product_tmpl_ids = [x['product_tmpl_id'][0] for x in product_tmpls if x]

            product_ids += product_obj.search(cr, uid, [('product_tmpl_id', 'in', product_tmpl_ids)], context=context)

        # treate only new poducts to add and no modification to existing products
        product_ids = set(product_ids) ^ set(already_added_product_ids)
        if not product_ids:
            return vals
        else:
            args += (tuple(product_ids),)

        query = '''
           SELECT sq.product_id as product_id,
                    pt.default_packaging as default_packaging,
                    pt.uom_id as product_uom_id,
                    sum(sq.qty) as product_qty,
                    sum(sq.qty)/COALESCE(pt.default_packaging,1.0) as packaging_qty,
                    sq.location_id as location_id
           FROM stock_quant sq
           INNER JOIN product_product pp ON ( sq.product_id = pp.id)
           INNER JOIN product_template pt ON ( pp.product_tmpl_id = pt.id)
           WHERE''' + domain + '''
           GROUP BY sq.product_id, pt.default_packaging, pt.uom_id,sq.location_id
        '''
        cr.execute(query, args)

        found_product_ids = []
        for product_line in cr.dictfetchall():
            product_line['inventory_id'] = inventory.id
            product_line['product_qty'] = 0.0 #Reset quantity to force the user to set the quantity manually
            vals.append(product_line)
            found_product_ids.append(product_line['product_id'])

        unfound_product_ids = list(set(product_ids) - set(found_product_ids))
        for product in product_obj.browse(cr, uid, unfound_product_ids, context):
            vals.append({
                'product_id': product.id,
                'default_packaging': product.default_packaging,
                'product_uom_id': product.uom_id.id,
                'packaging_qty': 0.0,
                'product_qty':0.0,
                'location_id': inventory.location_id.id,
                'inventory_id': inventory.id,
            })

        return vals

    def action_add_category_supplier(self, cr, uid, ids, context=None):
        _logger.info('------------------  action_add_category   -------------------')

        if not ids:
            raise osv.except_osv(('Error'),
                                 ("Please select an inventory to continue"))
        if len(ids) > 1:
            raise osv.except_osv(('Error'),
                                 ("You should on one inventory in the same time"))

        inventory_line_obj = self.pool.get('stock.inventory.line')

        inv = self.browse(cr, uid, ids[0], context=context)
        lines = self._coop_produce_get_inventory_lines(cr, uid, inv, context=context)

        for line in lines:
            inventory_line_obj.create(cr, uid, line, context=context)
        return True

    def action_reset(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            inv.line_ids.unlink()

    def init_with_theorical_qty(self,cr,uid,ids,context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            for line in inv.line_ids:
                line.write({'product_qty':line.packaging_qty*line.default_packaging,
                            'stock_qty':line.packaging_qty})


class StockInventoryLine(osv.osv):
    _inherit = "stock.inventory.line"

    def _get_qty_loss(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.qty_stock - line.packaging_qty
        return res

    _columns = {
        'default_packaging': fields.float(string='Default packaging', readonly=True),
        'packaging_qty': fields.float(string='Theorical packaging qty', readonly=True),
        'qty_loss': fields.function(_get_qty_loss, type="float", string='Quantity Lost',
                                    digits_compute=dp.get_precision('Product Unit of Measure'),
                                    help='Quantity Theoric Of Reference - Stock Quantity'),
        'qty_stock': fields.float(string='Stock Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
                                  help="Stock Quantity"),

    }

    def on_change_qty_stock(self, cr, uid, ids, product_id,packaging_qty=0.0, qty_stock=0.0, default_packaging=None, context=None):
        if not product_id:
            return self.on_change_product_id(cr,uid,ids,product_id=product_id)
        if not default_packaging:
            return {'warning': {'title': _('Warning: wrong default packaging'),
                                'message': _('The default packaging is not defined on the product')}
                    }
        else:
            return {'value': {'qty_loss': qty_stock - packaging_qty,
                              'product_qty': qty_stock * default_packaging}}

    def on_change_product_id(self, cr, uid, ids, product_id=None, context=None):
        if not product_id:
            return {'value': {'default_packaging': False,
                              'packaging_qty': False,
                              'qty_loss': False,
                              'product_qty': 0.0,
                              }}
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        default_packaging = product.default_packaging
        if default_packaging:
            packaging_qty = product.qty_available / default_packaging
            ret = {'value': {'default_packaging': default_packaging,
                             'packaging_qty': packaging_qty,
                             'qty_stock': 0.0,
                             'qty_loss': -packaging_qty,
                             'product_qty': 0.0
                             }}
        else:
            ret = {'value': {'default_packaging': 0.0,
                             'packaging_qty': 0.0,
                             'qty_stock': 0.0,
                             'qty_loss': 0.0,
                             'product_qty': 0.0
                             }}
            ret['warningn'] = {'title': _('Warning: wrong default packaging'),
                               'message': _('The default packaging is not defined on the product')}
        return ret
