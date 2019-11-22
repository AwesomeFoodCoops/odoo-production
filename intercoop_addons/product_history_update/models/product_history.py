# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job, related_action
import logging
_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = 'product.product'

    history_updated = fields.Boolean('History Updated', default=False)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def update_history(self):
        self.env['product.history'].update_products_history(self.mapped(
            'product_variant_ids').ids)
        # self.env['product.history'].update_product_history_script()
        return True

    @api.multi
    def calc_history(self):
        products = self.mapped('product_variant_ids')
        products._compute_history('months')
        products._compute_history('weeks')
        products._compute_history('days')
        return True


class ProductHistory(models.Model):
    _inherit = 'product.history'

    @api.model
    def get_products(self):
        sql = """select distinct ph.product_id from product_history ph
        left join product_product p on ph.product_id = p.id
        where p.history_updated = 'f' or p.history_updated is null"""
        self._cr.execute(sql)
        return [p[0] for p in self._cr.fetchall()]

    @api.model
    def update_product_history_script(self, product_ids=None):
        if not product_ids:
            product_ids = self.get_products()
        self.update_products_history(product_ids)
        return True

    @api.model
    def update_product_history_script_background(self, product_ids=None):
        if not product_ids:
            product_ids = self.get_products()
        self.product_history_update_background(product_ids)
        return True

    @api.model
    def update_products_history(self, product_ids):
        product_obj = self.env['product.product']
        for product_id in product_ids:
            _logger.info('Updating Product ID: %s' % product_id)
            try:
                for history_range in ['days', 'weeks', 'months']:
                    history_lines = self.search(
                        [('product_id', '=', product_id),
                         ('history_range', '=', history_range)],
                        order='from_date')
                    if history_lines:
                        sql = """
                                SELECT min(sm.id), sm.product_id,
                                date_trunc(%s, sm.date)::date,
                                    sum(sm.product_qty) as product_qty
                                FROM stock_move as sm, stock_location as orig,
                                    stock_location as dest
                                WHERE sm.location_id = orig.id and
                                    sm.location_dest_id = dest.id
                                    and sm.product_id = %s and
                                    sm.date >= %s and
                                    sm.date <= %s and
                                    dest.usage = 'inventory' and
                                    sm.state != 'cancel'
                                GROUP BY sm.product_id, date_trunc(%s,sm.date)
                                ORDER BY sm.product_id, date_trunc(%s,sm.date)
                                """
                        params = (history_range[:-1], product_id,
                                  history_lines[0].from_date,
                                  history_lines[-1].to_date + ' 23:59:59',
                                  history_range[:-1], history_range[:-1])
                        self.env.cr.execute(sql, params)
                        stock_moves = self.env.cr.fetchall()
                        stock_moves_dict = {}
                        for move in stock_moves:
                            # set sm.date as a key
                            stock_moves_dict[move[2]] = move
                        opening_qty = history_lines[0].start_qty
                        for line in history_lines:
                            move = stock_moves_dict.get(line.from_date, [])
                            if move:
                                loss_qty = -move[3]  # Loss Qty
                            else:
                                loss_qty = 0
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
                _logger.error('Error while updating a product ID: %s, %s' % (
                    product_id, str(e)))
        return True

    @api.model
    def product_history_update_background(self, product_ids):
        num_prod_per_job = 50
        splited_prod_list = \
            [product_ids[i: i + num_prod_per_job]
             for i in range(0, len(product_ids), num_prod_per_job)]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid,
                                   context=self.env.context)
        # Create jobs
        for product_list in splited_prod_list:
            create_job_to_update_product_history.delay(
                session, 'product.history', product_list, priority=1, eta=10)


def related_action_update_products_history(session, job):
    return session.env[job.args[0]].update_products_history(job.args[1])


@job
@related_action(action=related_action_update_products_history)
def create_job_to_update_product_history(session, model_name, product_ids):
    """ Job for Recomputing Loss Qty and Opening Qty of Product History """
    session.env[model_name].update_products_history(product_ids)
