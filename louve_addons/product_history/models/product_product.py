# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product - Average Consumption Module for Odoo
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
from datetime import date
from datetime import datetime as dt
from datetime import timedelta as td
from dateutil.relativedelta import relativedelta as rd

old_date = date(2015, 1, 1)

DAYS_IN_RANGE = {
    'days': 1,
    'weeks': 7,
    'months': 30,
}


class ProductProduct(models.Model):
    _inherit = "product.product"

# Column section
    product_tmpl_id = fields.Many2one(comodel_name='product.template')
    history_range = fields.Selection(related="product_tmpl_id.history_range",
                                     readonly=True)
    product_history_ids = fields.Many2many(
        comodel_name='product.history', inverse_name='product_id',
        string='History', compute="_compute_product_history_ids")
    number_of_periods_real = fields.Integer(
        'Number of History periods',
        help="""Number of valid history periods used for the calculation""")
    number_of_periods_target = fields.Integer(
        related='product_tmpl_id.number_of_periods')

# Private section
    @api.onchange(
        'history_range', 'product_history_ids', 'number_of_periods_target')
    @api.multi
    def _average_consumption(self):
        for product in self:
            if product.consumption_calculation_method == 'history':
                product._average_consumption_history()
        super(ProductProduct, self)._average_consumption()

    @api.depends('history_range')
    @api.multi
    def _compute_product_history_ids(self):
        for product in self:
            ph_ids = self.env['product.history'].search([
                ('product_id', '=', product.id),
                ('history_range', '=', product.history_range)])
            ph_ids = [ph.id for ph in ph_ids]
            product.product_history_ids = [(6, 0, ph_ids)]

    @api.multi
    def _compute_qtys(self, states=('done',)):
        domain = [('state', 'in', states)] + self._get_domain_dates()
        for product in self:
            domain_product = domain + [('product_id', '=', product.id)]
            res = {
                'purchase_qty': 0,
                'view_qty': 0,
                'sale_qty': 0,
                'inventory_qty': 0,
                'procurement_qty': 0,
                'production_qty': 0,
                'transit_qty': 0,
                'total_qty': 0, }
            move_pool = self.env['stock.move']

            for field, usage, sign in (
                    ('purchase_qty', 'supplier', 1),
                    ('sale_qty', 'customer', 1),
                    ('inventory_qty', 'inventory', 1),
                    ('procurement_qty', 'procurement', 1),
                    ('production_qty', 'production', 1),
                    ('transit_qty', 'transit', 1),
            ):
                moves = move_pool.read_group(domain_product + [
                    ('location_id.usage', '=', usage),
                    ('location_dest_id.usage', '=', 'internal'),
                ], ['product_qty'], [])
                for move in moves:
                    res[field] = sign * (move['product_qty'] or 0)
                    res['total_qty'] += sign * (move['product_qty'] or 0)
                moves = move_pool.read_group(domain_product + [
                    ('location_dest_id.usage', '=', usage),
                    ('location_id.usage', '=', 'internal'),
                ], ['product_qty'], [])
                for move in moves:
                    res[field] -= sign * (move['product_qty'] or 0)
                    res['total_qty'] -= sign * (move['product_qty'] or 0)
            return res

    @api.multi
    def _average_consumption_history(self):
        for product in self:
            nb = product.number_of_periods_target
            history_range = product.history_range
            history_ids = self.env['product.history'].search([
                ('product_id', '=', product.id),
                ('history_range', '=', history_range),
                ('ignored', '=', 0)]).sorted()
            nb = min(len(history_ids), nb)
            if nb == 0:
                product.total_consumption = 0
                product.average_consumption = 0
                product.number_of_periods_real = 0
            else:
                ids = range(nb)
                total_consumption = 0
                for id in ids:
                    total_consumption -= history_ids[id].sale_qty
                product.total_consumption = total_consumption
                product.average_consumption = total_consumption / nb /\
                    DAYS_IN_RANGE[product.history_range]
                product.number_of_periods_real = nb
                self._displayed_average_consumption()

# Action section
    @api.model
    def run_product_history_day(self):
        # This method is called by the cron task
        products = self.env['product.product'].search([
            '|', ('active', '=', True),
            ('active', '=', False)])
        products._compute_history('days')

    @api.model
    def run_product_history_week(self):
        # This method is called by the cron task
        products = self.env['product.product'].search([
            '|', ('active', '=', True),
            ('active', '=', False)])
        products._compute_history('weeks')

    @api.model
    def run_product_history_month(self):
        # This method is called by the cron task
        products = self.env['product.product'].search([
            '|', ('active', '=', True),
            ('active', '=', False)])
        products._compute_history('months')

    @api.model
    def init_history(self):
        products = self.env['product.product'].search([
            '|', ('active', '=', True),
            ('active', '=', False)])
        products._compute_history('months')
        products._compute_history('weeks')
        products._compute_history('days')

    @api.multi
    def _compute_history(self, history_range):
        now = date.today()
        for product in self:
            if history_range == "months":
                delta = rd(months=1)
            elif history_range == "weeks":
                delta = rd(weeks=1)
            else:
                delta = rd(days=1)
            history_ids = self.env['product.history'].search([
                ('history_range', '=', history_range),
                ('product_id', '=', product.id)])
            if history_ids:
                self.env.cr.execute(
                    """SELECT to_date, end_qty FROM product_history
                    WHERE product_id=%s AND history_range='%s'
                    ORDER BY "id" DESC LIMIT 1"""
                    % (product.id, history_range))
                last_record = self.env.cr.fetchone()
                last_date = last_record and dt.strptime(
                    last_record[0], "%Y-%m-%d").date() or old_date
                last_qty = last_record and last_record[1] or 0
                from_date = last_date + td(days=1)
            else:
                self.env.cr.execute(
                    """SELECT date FROM stock_move
                    WHERE product_id=%s ORDER BY "date" LIMIT 1"""
                    % (product.id))
                fetch = self.env.cr.fetchone()
                from_date = fetch and dt.strptime(
                    fetch[0].split(" ")[0], "%Y-%m-%d").date() or now
                if history_range == "months":
                    from_date = date(
                        from_date.year, from_date.month, 1)
                elif history_range == "weeks":
                    from_date = from_date - td(days=from_date.weekday())
                last_qty = 0
            while from_date + delta <= now:
                last_date = from_date + delta - td(days=1)
                res = product.with_context({
                    'from_date': dt.strftime(from_date, "%Y-%m-%d"),
                    'to_date': dt.strftime(last_date, "%Y-%m-%d")
                })._compute_qtys()
                res2 = product.with_context({
                    'to_date': dt.strftime(last_date, "%Y-%m-%d"),
                })._product_available()[product.id]
                res3 = product.with_context({
                    'to_date': dt.strftime(last_date, "%Y-%m-%d")
                })._compute_qtys()
                vals = {
                    'product_id': product.id,
                    'product_tmpl_id': product.product_tmpl_id.id,
                    'location_id': self.env['stock.location'].search([])[0].id,
                    'from_date': dt.strftime(from_date, "%Y-%m-%d"),
                    'to_date': dt.strftime(last_date, "%Y-%m-%d"),
                    'purchase_qty': res['purchase_qty'],
                    'sale_qty': res['sale_qty'],
                    'loss_qty': res['inventory_qty'],
                    'start_qty': last_qty,
                    'end_qty': res3['total_qty'],
                    'virtual_qty': res3['total_qty'] +
                    res2['incoming_qty'] - res2['outgoing_qty'],
                    'incoming_qty': res2['incoming_qty'],
                    'outgoing_qty': -res2['outgoing_qty'],
                    'history_range': history_range,
                }
                self.env['product.history'].create(vals)
                last_qty = res3['total_qty']
                from_date = last_date + td(days=1)
