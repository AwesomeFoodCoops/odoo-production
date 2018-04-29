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

from openerp.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class OrderWeekPlanning(models.Model):
    _name = "order.week.planning"
    _description = "Order Week Planning"

    _order = "year desc,week_number desc"

    @api.one
    @api.depends('date')
    def _get_planning_info(self):
        if not self.date:
            self.week_number = 0
            self.name = _('Week order planning number AAAA/XX')
            self.year = 0
        else:
            week_number = datetime.datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S").strftime("%W")
            self.week_number = week_number
            year = datetime.datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S").year
            self.name = _('Week order planning number %s/%s' % (year, week_number))
            self.year = year

    name = fields.Char(string="Name",
                       compute="_get_planning_info",
                       store=True,
                       help="The name Of Order Schedulling", )
    year = fields.Integer(string="Year",
                          compute="_get_planning_info",
                          store=True,
                          help="The year Of Order Schedulling")
    week_number = fields.Integer(string="Week Number",
                                 compute="_get_planning_info",
                                 store=True,
                                 help="Number of Inventory Week")
    date = fields.Datetime('Date', required=True)
    hide_initialisation = fields.Boolean(string="Hide initialisation area", help="Hide initialisation area")
    categ_ids = fields.Many2many('product.category')
    supplier_ids = fields.Many2many('res.partner', 'stock_inventory_res_partner', 'inventory_id', 'supplier_id',
                                    'Supplier', domain=[('supplier', '=', True), ('is_company', '=', True)],
                                    help="Specify Product Category to focus in your inventory.")

    date_stock = fields.Datetime('Date stock')

    line_ids = fields.One2many('order.week.planning.line', 'order_week_planning_id', 'Planning lines',
                               help="Planning lines per day")

    monday_ordered_qty = fields.Float("Monday's ordered qty",
                                      default=0.0,
                                      digits=dp.get_precision('Product Unit of Measure'))
    tuesday_ordered_qty = fields.Float("Tuesday's ordered qty",
                                       default=0.0,
                                       digits=dp.get_precision('Product Unit of Measure'))
    wednesday_ordered_qty = fields.Float("Wednesday's ordered qty",
                                         default=0.0,
                                         digits=dp.get_precision('Product Unit of Measure'))
    thirsday_ordered_qty = fields.Float("Thirsday's ordered qty",
                                        default=0.0,
                                        digits=dp.get_precision('Product Unit of Measure'))
    friday_ordered_qty = fields.Float("Friday's ordered qty",
                                      default=0.0,
                                      digits=dp.get_precision('Product Unit of Measure'))
    saturday_ordered_qty = fields.Float("Saturday's ordered qty",
                                        default=0.0,
                                        digits=dp.get_precision('Product Unit of Measure'))

    monday_received_qty = fields.Float("Monday's received qty",
                                       default=0.0,
                                       digits=dp.get_precision('Product Unit of Measure'))
    tuesday_received_qty = fields.Float("Tuesday's received qty",
                                        default=0.0,
                                        digits=dp.get_precision('Product Unit of Measure'))
    wednesday_received_qty = fields.Float("Wednesday's received qty",
                                          default=0.0,
                                          digits=dp.get_precision('Product Unit of Measure'))
    thirsday_received_qty = fields.Float("Thirsday's received qty",
                                         default=0.0,
                                         digits=dp.get_precision('Product Unit of Measure'))
    friday_received_qty = fields.Float("Friday's received qty",
                                       default=0.0,
                                       digits=dp.get_precision('Product Unit of Measure'))
    saturday_received_qty = fields.Float("Saturday's received qty",
                                         default=0.0,
                                         digits=dp.get_precision('Product Unit of Measure'))

    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             string='State',
                             readonly=True,
                             copy=False,
                             default='draft')

    week_total_receptions_qty = fields.Float("Total received qty",
                                             default=0.0,
                                             digits=dp.get_precision('Product Unit of Measure'))
    week_total_orders_qty = fields.Float("Total ordered qty",
                                         default=0.0,
                                         digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    def action_close_week(self):
        self.write({'state': 'done'})

    @api.multi
    def _coop_produce_get_planning_lines(self):
        self.ensure_one()
        vals = []

        products = self.env['product.product']
        supplier_infos = self.env['product.supplierinfo']
        product_already_added = self.env['product.product']

        for line in self.line_ids:
            product_already_added += line.product_id

        if self.categ_ids:
            products += products.search([('categ_id', 'in', self.categ_ids.ids)])

        if self.supplier_ids:
            supplier_infos += supplier_infos.search([('name', 'in', self.supplier_ids.ids)])
            product_tmpls = supplier_infos.read(['product_tmpl_id'])
            print product_tmpls
            product_tmpls_ids = [x['product_tmpl_id'][0] for x in product_tmpls]
            products += products.search([('product_tmpl_id', 'in', product_tmpls_ids)])

        products = products - product_already_added
        if not products:
            return vals

        for product in products:
            supplier_info = product.seller_ids and product.seller_ids[0] or False
            val = {
                'product_id': product.id,
                'supplier_id': supplier_info and supplier_info.name.id or False,
                'price_unit': supplier_info and supplier_info.price_taxes_excluded or 0.0,
                # set to this value because this value is used on purchase order
                'default_packaging': supplier_info.package_qty or 0,
                'start_inv': supplier_info.package_qty and product.qty_available / supplier_info.package_qty or 0.0,
                'order_week_planning_id': self.id,
            }
            vals.append(val)
        return vals

    @api.multi
    def action_add_products(self):
        self.ensure_one()
        planning_line_obj = self.env['order.week.planning.line']
        lines = self._coop_produce_get_planning_lines()

        for line in lines:
            planning_line_obj.create(line)

        return True

    @api.multi
    def action_reset(self):
        self.ensure_one()
        self.line_ids.unlink()

    @api.multi
    def action_week_receptions(self):
        raise UserError(_("Not yet implemented"))

    @api.multi
    def action_week_receptions(self):
        raise UserError(_("Not yet implemented"))


class OrderWeekPlanningLine(models.Model):
    _name = "order.week.planning.line"
    _description = "Order Week Planning Line"

    _order = 'week_year desc, week_number desc, product_name asc'

    @api.depends('start_inv', 'monday_qty', 'tuesday_qty', 'wednesday_qty', 'thirsday_qty', 'friday_qty',
                 'saturday_qty')
    def _get_kpi(self):
        return True

    week_year = fields.Integer(string="Week year",  # This field is used to order lines
                               related='order_week_planning_id.year',
                               store=True)
    week_number = fields.Integer(string="Week number",  # This field is used to order lines
                                 related='order_week_planning_id.week_number',
                                 store=True)
    product_name = fields.Char('Product name',
                               related="product_id.name",
                               store=True)  # This field is used to order lines

    order_week_planning_id = fields.Many2one('order.week.planning',
                                             string='Order week planning',
                                             ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product',
                                 required=True,
                                 select=True)

    default_packaging = fields.Float(string='Default packaging',
                                     required=True)
    sold_w_2_qty = fields.Float(string="Sold W-2",
                                compute="_get_kpi",
                                digits=dp.get_precision('Order Week Planning Precision'))
    sold_w_1_qty = fields.Float(string="Sold W-1",
                                compute="_get_kpi",
                                digits=dp.get_precision('Order Week Planning Precision'))
    total_qty = fields.Float(string="Total + S. Inv.",
                             compute="_get_kpi",
                             digits=dp.get_precision('Order Week Planning Precision'))
    sold_qty = fields.Float(string="Sold",
                            compute="_get_kpi",
                            digits=dp.get_precision('Order Week Planning Precision'))
    supplier_id = fields.Many2one('res.partner', 'Supplier',
                                  domain=[('supplier', '=', True), ('is_company', '=', True)])
    price_unit = fields.Float(string="Price U",
                              required=True)
    start_inv = fields.Float('S. Inv',
                             digits=dp.get_precision('Order Week Planning Precision'))
    monday_qty = fields.Float('Mond',
                              default=0.0,
                              digits=dp.get_precision('Order Week Planning Precision'))
    tuesday_qty = fields.Float('Tues',
                               default=0.0,
                               digits=dp.get_precision('Order Week Planning Precision'))
    wednesday_qty = fields.Float('Wed',
                                 default=0.0,
                                 digits=dp.get_precision('Order Week Planning Precision'))
    thirsday_qty = fields.Float('Thurs',
                                default=0.0,
                                digits=dp.get_precision('Order Week Planning Precision'))
    friday_qty = fields.Float('Fri',
                              default=0.0,
                              digits=dp.get_precision('Order Week Planning Precision'))
    saturday_qty = fields.Float('Sat',
                                default=0.0,
                                digits=dp.get_precision('Order Week Planning Precision'))
    end_inv_qty = fields.Float('E. Inv',
                               default=0.0,
                               digits=dp.get_precision('Order Week Planning Precision'))
    loss_qty = fields.Float('Loss',
                            default=0.0,
                            digits=dp.get_precision('Order Week Planning Precision'))
    medium_inventory_qty = fields.Float('Medium Qty',
                                        default=0.0,
                                        digits=dp.get_precision('Order Week Planning Precision'))

    _sql_constraints = [
        ('number_uniq', 'unique(week_number, product_id, default_packaging, supplier_id)',
         "You can't have two lines for the same, week, product, suppier and packaging!"),
    ]

    @api.onchange('supplier_id')
    def _onchange_supplier_id(self):
        if not self.supplier_id or not self.product_id:
            self.supplier_id = False
            self.price_unit = 0.0
            self.start_inv = 0.0
            self.default_packaging = 0.0
        else:

            supplier_info = self.env['product.supplierinfo'].search([('name', '=', self.supplier_id.id),
                                                                     ('product_tmpl_id', '=',
                                                                      self.product_id.product_tmpl_id.id)],
                                                                    limit=1)
            if supplier_info:
                self.price_unit = supplier_info[0].price_taxes_excluded
                self.default_packaging = supplier_info[0].package_qty
                self.start_inv = supplier_info[0].package_qty and self.product_id.qty_available / supplier_info[
                    0].package_qty or 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # look if a line of this product is already set
            if isinstance(self.id, models.NewId):
                # On NewId order_week_planning_id id not yet defined
                # In this case we get, the id passed in the context
                order_week_planning_id = self._context.get('default_order_week_planning_id')

                if order_week_planning_id:
                    line = self.search([('product_id', '=', self.product_id.id),
                                        ('order_week_planning_id', '=', self.order_week_planning_id.id),
                                        ], limit=1)
            else:
                line = self.search([('product_id', '=', self.product_id.id),
                                    ('order_week_planning_id', '=', self.order_week_planning_id.id),
                                    ('id', '!=', self.id),
                                    ], limit=1)
            self.supplier_id = False
            if not line:
                # Init the line with the right data
                supplier_info = self.product_id.seller_ids and self.product_id.seller_ids[0] or False
                if supplier_info:
                    self.supplier_id = supplier_info.name
                    self.price_unit = supplier_info.price_taxes_excluded
                    self.start_inv = supplier_info.package_qty and self.product_id.qty_available / supplier_info.package_qty or 0.0
                    self.default_packaging = supplier_info.package_qty

    def action_view_product_history(self):
        """ View History Product
        """
        line_ids = []
        for product in self:
            product_id = product.product_id.id
            default_packaging = product.default_packaging
            week_number = product.week_number
            order_ids = self.search([('product_id', '=', product_id),
                                     ('week_number', '<', week_number)])
            if order_ids:
                for order in order_ids:
                    _logger.info('-------------------------------------')
                    _logger.info(order)
                    order_line = self.browse(order)
                    line_ids.append(
                        (0, 0, {'semaine_nbre': order_line.order_id.week_number, 'prix_unitaire': order_line.list_price,
                                'monday_line': order_line.monday_line, 'tuesday_line': order_line.tuesday_line,
                                'wednesday_line': order_line.wednesday_line, 'thirsday_line': order_line.thirsday_line,
                                'friday_line': order_line.friday_line, 'saturday_line': order_line.saturday_line,
                                'total_inv': order_line.total_in, 'e_inv': order_line.e_in,
                                'loss': order_line.loss, 'sold': order_line.sold,
                                'inv_int': order_line.inv_int, 'e_inv': order_line.e_in,

                                }))

            view_id = self.env['ir.ui.view'].search([('model', '=', 'planification.product.history'),
                                                     ('name', '=', 'coop.product.product.history.form')])
            return {
                'name': "Historique Du Produit",
                'view_type': 'form',
                'res_model': 'planification.product.history',
                'view_id': view_id[0],
                'view_mode': 'form',
                'nodestroy': True,
                'target': 'current',
                'context': {'default_product_id': product_id, 'default_default_packaging': default_packaging,
                            'default_line_ids': line_ids},
                'flags': {'form': {'action_buttons': False}},
                'type': 'ir.actions.act_window',
            }
