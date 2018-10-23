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
from openerp import api, models, fields, _
import openerp.addons.decimal_precision as dp

from openerp.exceptions import UserError, Warning

import logging

_logger = logging.getLogger(__name__)


def get_date_from_week_number(year, week_num, offset):
    # offset = 0 : sunday, monday : 1, .... saturday = 6
    d = "%s-%s-%s" % (year, week_num, offset)
    r = datetime.datetime.strptime(d, "%Y-%W-%w")
    return r


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

    @api.multi
    def _compute_picking(self):
        for week_planning in self:
            date1 = get_date_from_week_number(week_planning.year, week_planning.week_number, 1)
            date2 = get_date_from_week_number(week_planning.year, week_planning.week_number, 6)
            product_ids = [l.product_id.id for l in week_planning.line_ids]

            pls = self.env['purchase.order.line'].search([('product_id', 'in', product_ids),
                                                          ('date_planned', '<=', date2.strftime("%Y-%m-%d")),
                                                          ('date_planned', '>=', date1.strftime("%Y-%m-%d")),
                                                          ])

            orders = list(set([l.order_id for l in pls]))
            pick_ids = []
            for order in orders:
                pick_ids += order.picking_ids.ids

            week_planning.week_total_receptions = len(list(set(pick_ids)))

    @api.multi
    def _compute_orders(self):
        for week_planning in self:
            date1 = get_date_from_week_number(week_planning.year, week_planning.week_number, 1)
            date2 = get_date_from_week_number(week_planning.year, week_planning.week_number, 6)
            product_ids = [l.product_id.id for l in week_planning.line_ids]

            pls = self.env['purchase.order.line'].search([('product_id', 'in', product_ids),
                                                          ('date_planned', '<=', date2.strftime("%Y-%m-%d")),
                                                          ('date_planned', '>=', date1.strftime("%Y-%m-%d")),
                                                          ])

            orders = list(set([l.order_id.id for l in pls]))
            week_planning.week_total_orders = len(orders)

    @api.multi
    def _get_kpi(self):
        # Compute   ,  ninvivgi_gvgi_v_çèonbj
        order_fields2sum = {
            1: 'monday_ordered_qty',
            2: 'tuesday_ordered_qty',
            3: 'wednesday_ordered_qty',
            4: 'thirsday_ordered_qty',
            5: 'friday_ordered_qty',
            6: 'saturday_ordered_qty'
        }

        received_fields2sum = {
            1: 'monday_received_qty',
            2: 'tuesday_received_qty',
            3: 'wednesday_received_qty',
            4: 'thirsday_received_qty',
            5: 'friday_received_qty',
            6: 'saturday_received_qty'
        }

        line_field2sum = {
            1: 'monday_qty',
            2: 'tuesday_qty',
            3: 'wednesday_qty',
            4: 'thirsday_qty',
            5: 'friday_qty',
            6: 'saturday_qty'
        }

        for week_planning in self:
            for day2sum in order_fields2sum:
                date = get_date_from_week_number(week_planning.year, week_planning.week_number, day2sum)
                line_date = date.strftime("%Y-%m-%d")
                now_str = datetime.datetime.now().strftime("%Y-%m-%d")
                if line_date > now_str:
                    week_planning[order_fields2sum[day2sum]] = sum(
                        [x[line_field2sum[day2sum]] for x in week_planning.line_ids])
                    week_planning[received_fields2sum[day2sum]] = sum(
                        [x[line_field2sum[day2sum]] for x in week_planning.line_ids])
                else:
                    product_ids = [l.product_id.id for l in week_planning.line_ids]

                    pls = self.env['purchase.order.line'].search([('product_id', 'in', product_ids),
                                                                  ('date_planned', '=', line_date),
                                                                  ('state', 'not in', ['draft', 'cancel'])
                                                                  ])
                    week_planning[order_fields2sum[day2sum]] = sum([x.product_qty_package for x in pls], 0.0)

                    orders = list(set([x.order_id for x in pls]))
                    picking_ids = []
                    for o in orders:
                        picking_ids += o.picking_ids.ids

                    if not picking_ids:
                        week_planning[order_fields2sum[day2sum]] = 0.0
                    else:
                        sps = self.env['stock.picking'].search([('id', 'in', picking_ids),
                                                                ('min_date', 'like', '%s%%' % line_date),
                                                                ])
                        total = 0.0
                        for sp in sps:
                            total += sum([x.qty_done_package for x in sp.pack_operation_product_ids], 0.0)
                        week_planning[received_fields2sum[day2sum]] = total

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
    date = fields.Datetime('Date', required=True, copy=False)
    hide_initialisation = fields.Boolean(string="Hide initialisation area", help="Hide initialisation area")
    categ_ids = fields.Many2many('product.category')
    supplier_ids = fields.Many2many('res.partner', 'stock_inventory_res_partner', 'inventory_id', 'supplier_id',
                                    'Supplier', domain=[('supplier', '=', True), ('is_company', '=', True)],
                                    help="Specify Product Category to focus in your inventory.")

    date_stock = fields.Datetime('Date stock')

    line_ids = fields.One2many('order.week.planning.line', 'order_week_planning_id', 'Planning lines',
                               help="Planning lines per day", ondelete='cascade', copy=True)

    monday_ordered_qty = fields.Float("Monday's ordered qty",
                                      default=0.0,
                                      compute="_get_kpi",
                                      digits=dp.get_precision('Product Unit of Measure'))
    tuesday_ordered_qty = fields.Float("Tuesday's ordered qty",
                                       default=0.0,
                                       compute="_get_kpi",
                                       digits=dp.get_precision('Product Unit of Measure'))
    wednesday_ordered_qty = fields.Float("Wednesday's ordered qty",
                                         default=0.0,
                                         compute="_get_kpi",
                                         digits=dp.get_precision('Product Unit of Measure'))
    thirsday_ordered_qty = fields.Float("Thirsday's ordered qty",
                                        default=0.0,
                                        compute="_get_kpi",
                                        digits=dp.get_precision('Product Unit of Measure'))
    friday_ordered_qty = fields.Float("Friday's ordered qty",
                                      default=0.0,
                                      compute="_get_kpi",
                                      digits=dp.get_precision('Product Unit of Measure'))
    saturday_ordered_qty = fields.Float("Saturday's ordered qty",
                                        default=0.0,
                                        compute="_get_kpi",
                                        digits=dp.get_precision('Product Unit of Measure'))

    monday_received_qty = fields.Float("Monday's received qty",
                                       default=0.0,
                                       compute="_get_kpi",
                                       digits=dp.get_precision('Product Unit of Measure'))
    tuesday_received_qty = fields.Float("Tuesday's received qty",
                                        default=0.0,
                                        compute="_get_kpi",
                                        digits=dp.get_precision('Product Unit of Measure'))
    wednesday_received_qty = fields.Float("Wednesday's received qty",
                                          default=0.0,
                                          compute="_get_kpi",
                                          digits=dp.get_precision('Product Unit of Measure'))
    thirsday_received_qty = fields.Float("Thirsday's received qty",
                                         default=0.0,
                                         compute="_get_kpi",
                                         digits=dp.get_precision('Product Unit of Measure'))
    friday_received_qty = fields.Float("Friday's received qty",
                                       default=0.0,
                                       compute="_get_kpi",
                                       digits=dp.get_precision('Product Unit of Measure'))
    saturday_received_qty = fields.Float("Saturday's received qty",
                                         default=0.0,
                                         compute="_get_kpi",
                                         digits=dp.get_precision('Product Unit of Measure'))

    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             string='State',
                             readonly=True,
                             copy=False,
                             default='draft')

    week_total_receptions = fields.Integer("Total receptions",
                                           default=0,
                                           compute='_compute_picking')
    week_total_orders = fields.Integer("Total orders",
                                       default=0,
                                       compute='_compute_orders')


    @api.multi
    def action_generate_next_week(self):
        self.ensure_one()

        new_date = get_date_from_week_number(self.year, self.week_number,0)
        new_date = new_date + datetime.timedelta(days=7)
        new_date_str = new_date.strftime("%Y-%m-%d")
        new_id = self.copy({'date':new_date_str})
        new_id.action_update_start_inventory()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'order.week.planning',
            'res_id': new_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

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
                'default_packaging': product.default_packaging or 0,
                'supplier_packaging': supplier_info.package_qty or 0,
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
    def unlink(self):
        for p in self:
            if p.state != 'draft':
                raise UserError(_("It's not allowed to delete a vaalidated order planining"))
            else:
                super(OrderWeekPlanning,self).unlink()

    @api.multi
    def action_update_start_inventory(self):
        self.ensure_one()
        for line in self.line_ids:
            if  line.default_packaging == 0.0:
                raise UserError(_("The product %s has no default packaging set") % (line.product_id.name,))
            line.default_packaging = line.product_id.default_packaging
            line.start_inv = line.product_id.qty_available / line.default_packaging

    @api.multi
    def action_view_orders(self):
        self.ensure_one()

        date1 = get_date_from_week_number(self.year, self.week_number, 1)
        date2 = get_date_from_week_number(self.year, self.week_number, 6)
        product_ids = [l.product_id.id for l in self.line_ids]

        pls = self.env['purchase.order.line'].search([('product_id', 'in', product_ids),
                                                      ('date_planned', '<=', date2.strftime("%Y-%m-%d")),
                                                      ('date_planned', '>=', date1.strftime("%Y-%m-%d")),
                                                      ])

        order_ids = list(set([l.order_id.id for l in pls]))
        action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]

        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        # choose the view_mode accordingly
        if len(order_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, order_ids)) + "])]"
        elif len(order_ids) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = order_ids and order_ids[0] or False
        return result

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given week planning
        When only one found, show the picking immediately.
        '''
        self.ensure_one()

        date1 = get_date_from_week_number(self.year, self.week_number, 1)
        date2 = get_date_from_week_number(self.year, self.week_number, 6)
        product_ids = [l.product_id.id for l in self.line_ids]

        pls = self.env['purchase.order.line'].search([('product_id', 'in', product_ids),
                                                      ('date_planned', '<=', date2.strftime("%Y-%m-%d")),
                                                      ('date_planned', '>=', date1.strftime("%Y-%m-%d")),
                                                      ])

        orders = list(set([l.order_id for l in pls]))
        pick_ids = []
        for order in orders:
            pick_ids += order.picking_ids.ids

        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        # choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result

    @api.multi
    def action_other_weeks(self):
        self.ensure_one()

        lines = self.env['order.week.planning.line'].search(
            ['|', ('week_year', '<', self.year), '&', ('week_year', '=', self.year),
             ('week_number', '<=', self.week_number),
             ])

        tree_view = self.env.ref('coop_produce.view_order_week_planning_line_tree')
        search_view = self.env.ref('coop_produce.view_order_week_planning_line_search')

        result = {
            'name': _("Product history"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': tree_view.id,
            'search_view_id': search_view.id,
            'context': {'search_default_group_by_year': 1},
            'domain': [('id', 'in', lines.ids)],
            'target': 'current',
            'res_model': 'order.week.planning.line',
        }

        return result

    @api.multi
    def _get_lines_grouped_per_supplier(self):
        self.ensure_one()
        line_grouped_by_supplier = {}
        for line in self.line_ids:
            if line.supplier_id in line_grouped_by_supplier:
                line_grouped_by_supplier[line.supplier_id] += line
            else:
                line_grouped_by_supplier[line.supplier_id] = line
        return line_grouped_by_supplier

    @api.multi
    def create_purchase_orders(self):
        self.ensure_one()
        day_num = self._context.get('day_number', 0)
        order_date = get_date_from_week_number(self.year, self.week_number, day_num)
        supplier_lines = self._get_lines_grouped_per_supplier()
        supplier_ids = [p.id for p in supplier_lines.keys()]
        str_date_order = order_date.strftime("%Y-%m-%d")
        str_origin = _("Order Plan Week %s/%s" % (self.year, self.week_number))
        orders = self.env['purchase.order'].search([('partner_id', 'in', supplier_ids),
                                                    ('date_order', '=', str_date_order),
                                                    ('state', '=', 'draft'),
                                                    ('origin', 'like', str_origin)])

        # unlink all draft orders generated automatically for the same day
        orders.button_cancel()
        orders.unlink()
        po_line_obj = self.env['purchase.order.line']
        for supplier in supplier_lines:
            fpos = self.env['account.fiscal.position'].with_context(
                company_id=self.env.user.company_id.id).get_fiscal_position(
                supplier.id)

            po_vals = {
                'partner_id': supplier.id,
                'date_order': str_date_order,
                'date_planned': str_date_order,
                'origin': str_origin,
                'fiscal_position_id': fpos,
                # 'order_line': [(0, 0, line) for line in lines]
            }
            new_purchase = self.env['purchase.order'].create(po_vals)

            lines = supplier_lines[supplier].convert2order_line_vals(day_num, order_date, fpos)

            for line in lines:
                line['order_id'] = new_purchase.id
                new_line = po_line_obj.create(line)
                new_line._compute_amount()


class OrderWeekPlanningLine(models.Model):
    _name = "order.week.planning.line"
    _description = "Order Week Planning Line"

    _order = 'week_year desc, week_number desc, product_name asc'

    @api.depends('start_inv', 'monday_qty', 'tuesday_qty', 'wednesday_qty', 'thirsday_qty', 'friday_qty',
                 'saturday_qty', 'end_inv_qty', 'loss_qty','default_packaging')
    def _get_kpi(self):
        # Compute
        fields2sum = ['monday_qty', 'tuesday_qty', 'wednesday_qty', 'thirsday_qty', 'friday_qty',
                      'saturday_qty']
        for line in self:
            w_1_qty = line.get_previous_solde_qty(-1)
            w_2_qty = line.get_previous_solde_qty(-2)
            #line.start_inv = line.start_inv * line.product_id.default_packaging/line.default_packaging
            line.total_qty = sum([line[x] for x in fields2sum]) + line.start_inv
            line.sold_qty = line.total_qty - line.end_inv_qty - line.loss_qty
            line.sold_w_1_qty = w_1_qty
            line.sold_w_2_qty = w_2_qty

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

    default_packaging = fields.Float(string='Default packaging', related='product_id.default_packaging')
    supplier_packaging = fields.Float(string='Supplier packaging',
                                      required=True)
    price_policy = fields.Selection(
        [('uom', 'per UOM'), ('package', 'per Package')], "Price Policy",
        default='uom', required=True, readonly=True)
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
    monday_qty = fields.Float('Mon.',
                              default=0.0,
                              digits=dp.get_precision('Order Week Planning Precision'),
                              copy=False)
    tuesday_qty = fields.Float('Tue.',
                               default=0.0,
                               digits=dp.get_precision('Order Week Planning Precision'),
                              copy=False)
    wednesday_qty = fields.Float('Wed.',
                                 default=0.0,
                                 digits=dp.get_precision('Order Week Planning Precision'),
                              copy=False)
    thirsday_qty = fields.Float('Thi.',
                                default=0.0,
                                digits=dp.get_precision('Order Week Planning Precision'),
                              copy=False)
    friday_qty = fields.Float('Fri.',
                              default=0.0,
                              digits=dp.get_precision('Order Week Planning Precision'),
                              copy=False)
    saturday_qty = fields.Float('Sat.',
                                default=0.0,
                                digits=dp.get_precision('Order Week Planning Precision'),
                              copy=False)
    end_inv_qty = fields.Float('E. Inv',
                               default=0.0,
                               digits=dp.get_precision('Order Week Planning Precision'),
                              copy=False)
    loss_qty = fields.Float('Loss',
                            default=0.0,
                            digits=dp.get_precision('Order Week Planning Precision'),
                              copy=False)
    medium_inventory_qty = fields.Float('Med',
                                        default=0.0,
                                        digits=dp.get_precision('Order Week Planning Precision'),
                              copy=False)

    _sql_constraints = [
        ('unique_line_per_product',
         'unique (week_year, week_number, product_id, supplier_id)',
         "You can't have two lines for the same, week, product and suppier !"),
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
                self.price_unit = supplier_info[0].base_price
                self.price_policy = supplier_info[0].price_policy
                self.supplier_packaging = supplier_info[0].package_qty
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
                    self.price_unit = supplier_info.base_price
                    self.price_policy = supplier_info.price_policy
                    self.start_inv = supplier_info.package_qty and self.product_id.qty_available / supplier_info.package_qty or 0.0
                    self.supplier_packaging = supplier_info.package_qty
                    self.default_packaging = self.product_id.default_packaging

    def convert2order_line_vals(self, day, date_planned, fpos):
        ret = []
        DAYS_NUMM = {
            1: 'monday_qty',
            2: 'tuesday_qty',
            3: 'wednesday_qty',
            4: 'thirsday_qty',
            5: 'friday_qty',
            6: 'saturday_qty',
        }
        for line in self:
            if line[DAYS_NUMM[day]] <= 0.0:
                continue
            taxes = line.product_id.supplier_taxes_id
            taxes_id = fpos.map_tax(taxes) if fpos else taxes
            if taxes_id:
                taxes_id = taxes_id.filtered(lambda x: x.company_id.id == self.env.user.company_id.id)

            line_val = {
                'product_id': line.product_id.id,
                'name': line.product_id.description_purchase or line.product_id.name,
                'product_qty': line.supplier_packaging * line[DAYS_NUMM[day]],
                'product_qty_package': line[DAYS_NUMM[day]],
                'package_qty': line.supplier_packaging,
                'product_uom': line.product_id.uom_po_id.id,
                'price_unit': line.price_unit,
                'price_policy': line.price_policy,
                'date_planned': date_planned.strftime("%Y-%m-%d"),
                'taxes_id': [(6, 0, taxes_id.ids)],
            }

            ret.append(line_val)
        return ret

    @api.multi
    def action_update_unit_price(self):
        raise UserError(_("Not yet implemented"))

    @api.multi
    def action_update_supplier_packaging(self):
        self.ensure_one()
        supplier_info = self.env['product.supplierinfo'].search([
            ('name', '=', self.supplier_id.id),
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)
        ])
        supplier_info.write({'package_qty': self.supplier_packaging})
        return True

    @api.multi
    def action_product_history_view(self):
        self.ensure_one()

        lines = self.search([('product_id', '=', self.product_id.id),
                             '|', ('week_year', '<', self.week_year), '&', ('week_year', '=', self.week_year),
                             ('week_number', '<=', self.week_number),
                             ])

        form_view = self.env.ref('coop_produce.view_coop_produce_historique_product_form')

        result = {
            'name': _("Product history"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_view.id,
            'context':{'line_ids':lines.ids,'product_id':self.product_id.id},
            #'domain': [('id', 'in', lines.ids)],
            #'target': 'new',
            'res_model': 'planification.product.history',
        }

        return result

    @api.multi
    def get_previous_solde_qty(self, week_gap, default_package = 1):
        self.ensure_one()
        current_date = get_date_from_week_number(self.week_year, self.week_number, 0)
        day_delta = 7 * week_gap
        new_date = current_date + datetime.timedelta(days=day_delta)
        new_year = new_date.year
        new_week_num = int(new_date.strftime("%W"))
        lines = self.search([('product_id', '=', self.product_id.id),
                             ('week_number', '=', new_week_num),
                             ('week_year', '=', new_year),
                             ])
        if lines:
            return sum(x.sold_qty * (x.default_packaging/default_package) for x in lines)
        else:
            return 0.0
