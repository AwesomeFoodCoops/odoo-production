# *- encoding: utf-8 -*-
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
from openerp import SUPERUSER_ID
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job, related_action
from collections import defaultdict

import logging
logger = logging.getLogger('openerp.louve_change_translation')

HISTORY_RANGE = [
    ('days', 'Days'),
    ('weeks', 'Week'),
    ('months', 'Month'),
]


class ProductHistory(models.Model):
    _name = "product.history"
    _order = 'from_date desc'

# Columns section
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product',
        required=True, ondelete='cascade')
    company_id = fields.Many2one(
        'res.company', related='product_id.company_id')
    product_tmpl_id = fields.Many2one(
        'product.template', related='product_id.product_tmpl_id',
        string='Template', store=True)
    location_id = fields.Many2one(
        'stock.location', string='Location', required=True,
        ondelete='cascade')
    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
    purchase_qty = fields.Float("Purchases", default=0)
    production_qty = fields.Float("Production", default=0)
    sale_qty = fields.Float("Sales", default=0)
    loss_qty = fields.Float("Losses", default=0)
    start_qty = fields.Float("Opening quantity", default=0)
    end_qty = fields.Float("Closing quantity", default=0)
    incoming_qty = fields.Float("Incoming quantity", default=0)
    outgoing_qty = fields.Float("Outgoing quantity", default=0)
    virtual_qty = fields.Float("Virtual quantity", default=0)
    ignored = fields.Boolean("Ignored", default=False)
    history_range = fields.Selection(
        HISTORY_RANGE, "History range",
        required=True)

    _sql_constraints = [
        ('history_uniq', 'unique(\
            product_id, location_id, from_date, to_date,\
            history_range)', 'This history line already exists!'),
    ]

# Private section
    @api.multi
    def mark_line(self, ignored=True):
        for line in self:
            line.ignored = ignored
            line.product_id.product_tmpl_id._compute_average_consumption()

    @api.multi
    def ignore_line(self):
        self.mark_line(True)
        return True

    @api.multi
    def unignore_line(self):
        self.mark_line(False)

    @api.model
    def create(self, vals):
        if vals.get('history_range') == 'weeks' and\
                vals.get('sale_qty', 0) == 0:
            vals['ignored'] = True
        return super(ProductHistory, self).create(vals)

    @api.model
    def get_products(self):
        sql = """select distinct ph.product_id from product_history ph
        left join product_product p on ph.product_id = p.id
        where p.history_updated = 'f' or p.history_updated is null"""
        self.env.cr.execute(sql)
        return [p[0] for p in self.env.cr.fetchall()]

    @api.model
    def update_products_history(self, product_ids):
        product_obj = self.env['product.product']
        product_history_obj = self.env['product.history']
        for product_id in product_ids:
            logger.info('Updating Product ID: %s' % product_id)
            try:
                for history_range in ['days', 'weeks', 'months']:
                    history_lines = product_history_obj.search(
                        [('product_id', '=', product_id),
                         ('history_range', '=', history_range)],
                        order='from_date')
                    if history_lines:
                        sql = """
                            SELECT date_trunc(%s, sm.date)::date,
                                orig.usage usage,
                                CASE WHEN orig.usage = 'inventory'
                                THEN SUM(sm.product_qty)
                                ELSE -sum(sm.product_qty) END product_qty
                            FROM stock_move as sm, stock_location as orig,
                                stock_location as dest
                            WHERE sm.location_id = orig.id and
                                sm.location_dest_id = dest.id
                                and sm.product_id = %s and
                                sm.date >= %s and
                                sm.date <= %s and
                                (dest.usage = 'inventory' or
                                 orig.usage = 'inventory') and
                                sm.state = 'done'
                            GROUP BY date_trunc(%s,sm.date), orig.usage
                            ORDER BY date_trunc(%s,sm.date)
                                """
                        params = (history_range[:-1], product_id,
                                  history_lines[0].from_date,
                                  history_lines[-1].to_date + ' 23:59:59',
                                  history_range[:-1], history_range[:-1])
                        self.env.cr.execute(sql, params)
                        stock_moves = self.env.cr.fetchall()
                        stock_moves_dict = defaultdict(float)
                        for move in stock_moves:
                            # set sm.date as a key
                            stock_moves_dict[move[0]] += move[2]
                        opening_qty = history_lines[0].start_qty
                        for line in history_lines:
                            loss_qty = stock_moves_dict.get(line.from_date, 0)
                            end_qty = opening_qty + line.purchase_qty + \
                                line.sale_qty + loss_qty
                            line.write({'start_qty': opening_qty,
                                        'loss_qty': loss_qty,
                                        'end_qty': end_qty,
                                        'virtual_qty':
                                            end_qty + line.incoming_qty +
                                            line.outgoing_qty})
                            opening_qty = end_qty
                product_obj.browse(product_id).write({'history_updated': True})

            except Exception as e:
                logger.error('Error while updating a product ID: %s, %s' % (
                    product_id, str(e)))
        return True

    @api.model
    def product_history_update_background(self):
        session = ConnectorSession(self._cr, SUPERUSER_ID)
        product_ids = self.get_products()
        num_prod_per_job = 50
        splitted_prod_list = [product_ids[i: i + num_prod_per_job]
                              for i in range(0, len(product_ids),
                                             num_prod_per_job)]
        # Create jobs
        for product_list in splitted_prod_list:
            create_job_to_update_product_history.delay(
                session, 'product.history', product_list, priority=1,
                eta=10)


@job
def create_job_to_update_product_history(session, model_name, product_ids):
    """ Job for Recomputing Loss Qty and Opening Qty of Product History """
    session.env[model_name].update_products_history(product_ids)
