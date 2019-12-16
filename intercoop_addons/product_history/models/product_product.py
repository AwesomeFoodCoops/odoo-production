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
from datetime import date, time
from datetime import datetime as dt
from datetime import timedelta as td
from dateutil.relativedelta import relativedelta as rd
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job


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
    last_history_day = fields.Many2one(
        string='last day history record', comodel_name='product.history',)
    last_history_week = fields.Many2one(
        string='last day history record', comodel_name='product.history',)
    last_history_month = fields.Many2one(
        string='last day history record', comodel_name='product.history',)
    history_updated = fields.Boolean('History Updated', default=False)

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

        product_ids = products.ids

        # Split product list in multiple parts
        num_prod_per_job = 50
        splited_prod_list = \
            [product_ids[i: i + num_prod_per_job]
             for i in range(0, len(product_ids), num_prod_per_job)]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid,
                                   context=self.env.context)
        # Create jobs
        for product_list in splited_prod_list:
            job_compute_history.delay(
                session, 'product.product', 'weeks', product_list)

    @api.model
    def run_recompute_6weeks_product_history(self):
        # This method is called by the cron task
        products = self.env['product.product'].search([
            '|', ('active', '=', True),
            ('active', '=', False)])

        product_ids = products.ids

        # Split product list into multiple parts
        num_prod_per_job = 50
        splited_prod_list = \
            [product_ids[i: i + num_prod_per_job]
             for i in range(0, len(product_ids), num_prod_per_job)]
        # Prepare session for job
        session = ConnectorSession(
            self._cr, self._uid, context=self.env.context)
        # Create jobs
        for product_list in splited_prod_list:
            job_recompute_last_6weeks_history.delay(
                session, 'product.product', 'weeks', product_list)

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
        to_date = date.today()
        if history_range == "months":
            delta = rd(months=1)
        elif history_range == "weeks":
            delta = rd(weeks=1)
        else:
            delta = rd(days=1)
        last_dates = {}
        last_qtys = {}
        product_ids = []
        for product in self:
            product_ids.append(product.id)
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
                    fetch[0].split(" ")[0], "%Y-%m-%d").date() or to_date
                if history_range == "months":
                    from_date = date(
                        from_date.year, from_date.month, 1)
                elif history_range == "weeks":
                    from_date = from_date - td(days=from_date.weekday())
                last_qty = 0
            last_dates[product.id] = from_date
            last_qtys[product.id] = last_qty

        product_ids.sort()
        last_date = min(last_dates.values())

        sql = """
            SELECT min(sm.id), sm.product_id, date_trunc('day',sm.date),
            sm.state, sum(sm.product_qty) as product_qty, orig.usage,
            dest.usage
            FROM stock_move as sm, stock_location as orig,
            stock_location as dest
            WHERE sm.location_id = orig.id and sm.location_dest_id = dest.id
            and sm.product_id in %s and sm.date >= %s and sm.state != 'cancel'
            GROUP BY sm.product_id, date_trunc('day',sm.date),
            sm.state, orig.usage, dest.usage
            ORDER BY sm.product_id, date_trunc('day',sm.date)
        """
        params = (tuple(product_ids), fields.Datetime.to_string(last_date))
        self.env.cr.execute(sql, params)
        stock_moves = self.env.cr.fetchall()

        for product_id in product_ids:
            stock_moves_product = []

            while len(stock_moves):
                if stock_moves[0][1] == product_id:
                    stock_moves_product.append(stock_moves.pop(0))
                else:
                    break

            if not stock_moves_product:
                continue

            product = self.env['product.product'].browse(product_id)
            from_date = last_dates.get(product_id, old_date)
            last_qty = last_qtys.get(product_id, 0)
            history_id = False

            while from_date + delta <= to_date:
                stock_moves_product_dates = []
                start_qty = last_qty
                last_date = from_date + delta - td(days=1)
                purchase_qty = sale_qty = loss_qty = 0
                incoming_qty = outgoing_qty = 0

                i_move = 0
                while i_move < len(stock_moves_product):
                    if stock_moves_product[i_move][2] >=\
                            fields.Datetime.to_string(from_date) and\
                            stock_moves_product[i_move][2] <=\
                            fields.Datetime.to_string(last_date):
                        stock_moves_product_dates.append(
                            stock_moves_product.pop(i_move))
                    else:
                        i_move += 1

                for move in stock_moves_product_dates:
                    if move[3] == 'done':
                        if move[5] == 'internal':
                            if move[6] == 'supplier':
                                purchase_qty -= move[4]
                            elif move[6] == 'customer':
                                sale_qty -= move[4]
                            elif move[6] == 'inventory':
                                loss_qty -= move[4]
                        elif move[6] == 'internal':
                            if move[5] == 'supplier':
                                purchase_qty += move[4]
                            elif move[5] == 'customer':
                                sale_qty += move[4]
                            elif move[5] == 'inventory':
                                loss_qty += move[4]
                    else:
                        if move[5] == 'internal':
                            if move[6] == 'supplier':
                                incoming_qty -= move[4]
                            elif move[6] == 'customer':
                                outgoing_qty -= move[4]
                            elif move[6] == 'inventory':
                                outgoing_qty -= move[4]
                        elif move[6] == 'internal':
                            if move[5] == 'supplier':
                                incoming_qty += move[4]
                            elif move[5] == 'customer':
                                outgoing_qty += move[4]
                            elif move[5] == 'inventory':
                                outgoing_qty += move[4]

                last_qty = start_qty + purchase_qty + sale_qty + loss_qty

                vals = {
                    'product_id': product_id,
                    'product_tmpl_id': product.product_tmpl_id.id,
                    'location_id': self.env['stock.location'].search([])[0].id,
                    'from_date': dt.strftime(from_date, "%Y-%m-%d"),
                    'to_date': dt.strftime(last_date, "%Y-%m-%d"),
                    'purchase_qty': purchase_qty,
                    'sale_qty': sale_qty,
                    'loss_qty': loss_qty,
                    'start_qty': start_qty,
                    'end_qty': last_qty,
                    'virtual_qty': last_qty + incoming_qty + outgoing_qty,
                    'incoming_qty': incoming_qty,
                    'outgoing_qty': outgoing_qty,
                    'history_range': history_range,
                }
                history_id = self.env['product.history'].create(vals)
                from_date = last_date + td(days=1)

            if history_id:
                if history_range == "months":
                    product.last_history_month = history_id.id
                elif history_range == "weeks":
                    product.last_history_week = history_id.id
                else:
                    product.last_history_day = history_id.id

    @api.multi
    def recompute_last_6weeks_history(self):
        for product in self:
            history_ids = self.env['product.history'].search([
                ('history_range', '=', 'weeks'),
                ('product_id', '=', product.id)
            ], order="id desc", limit=7)
            if history_ids:
                length = len(history_ids)
                last_6weeks_histories = history_ids[:6]
                past_7th_history = history_ids[-1]

                # Remove the last 6 weeks histories
                last_6weeks_histories.unlink()

                if length == 7:
                    to_date = past_7th_history.to_date
                    to_date_dt = fields.Date.from_string(to_date)
                    ending_qty = product.get_stock_inventory_at(
                        to_date_dt).get(product.id, 0)
                    past_7th_history.write(dict(end_qty=ending_qty))

    @api.multi
    def get_stock_inventory_at(self, at_date=False):
        values = {}
        if not at_date:
            at_date = fields.Datetime.now()
        elif isinstance(at_date, date):
            at_date = dt.combine(at_date, time(23, 59, 59))

        if isinstance(at_date, dt):
            at_date = fields.Datetime.to_string(at_date)

        query = """
SELECT product_id, sum(quantity) AS quantity
FROM   
(
    (
        SELECT sum(quant.qty) AS quantity,
                stock_move.product_id AS product_id
        FROM   stock_quant AS quant
        JOIN stock_quant_move_rel
            ON stock_quant_move_rel.quant_id = quant.id
        JOIN stock_move
            ON stock_move.id = stock_quant_move_rel.move_id
        JOIN stock_location dest_location
            ON stock_move.location_dest_id = dest_location.id
        JOIN stock_location source_location
            ON stock_move.location_id = source_location.id
        WHERE  quant.qty > 0
            AND stock_move.state = 'done'
            AND dest_location.usage IN ( 'internal', 'transit' )
            AND ( NOT ( source_location.company_id IS NULL
                        AND dest_location.company_id IS NULL )
                    OR source_location.company_id != dest_location.company_id
                    OR source_location.usage NOT IN ( 'internal', 'transit' )
                )
            AND stock_move.date <= %s
            AND stock_move.product_id = %s
         GROUP  BY stock_move.product_id
    )
    UNION ALL
    (
        SELECT sum(-quant.qty)       AS quantity,
                stock_move.product_id AS product_id
        FROM   stock_quant AS quant
        JOIN stock_quant_move_rel
            ON stock_quant_move_rel.quant_id = quant.id
        JOIN stock_move
            ON stock_move.id = stock_quant_move_rel.move_id
        JOIN stock_location source_location
            ON stock_move.location_id = source_location.id
        JOIN stock_location dest_location
            ON stock_move.location_dest_id = dest_location.id
        WHERE  quant.qty > 0
            AND stock_move.state = 'done'
            AND source_location.usage IN ( 'internal', 'transit' )
            AND ( NOT ( dest_location.company_id IS NULL
                        AND source_location.company_id IS NULL )
                    OR dest_location.company_id != source_location.company_id
                    OR dest_location.usage NOT IN ( 'internal', 'transit' ) 
                )
            AND stock_move.date <= %s
            AND stock_move.product_id = %s
        GROUP  BY stock_move.product_id
    )
) AS foo
GROUP  BY product_id

"""
        for product in self:
            product.env.cr.execute(
                query, (at_date, product.id, at_date, product.id))
            result = product.env.cr.fetchall()
            values[product.id] = result and result[0][1] or 0

        return values


@job
def job_compute_history(session, model_name, history_range, product_ids):
    """ Job for Computing Product History """
    products = session.env[model_name].browse(product_ids)
    products._compute_history(history_range)


@job
def job_recompute_last_6weeks_history(session, model_name, history_range, product_ids):
    """ Job for Recompute the last 6 weeks Product History """
    products = session.env[model_name].browse(product_ids)
    products.recompute_last_6weeks_history()
