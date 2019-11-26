# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job, related_action
from collections import defaultdict

import logging
logger = logging.getLogger('openerp.louve_change_translation')


def get_products(session):
    sql = """select distinct ph.product_id from product_history ph
    left join product_product p on ph.product_id = p.id
    where p.history_updated = 'f' or p.history_updated is null"""
    session.env.cr.execute(sql)
    return [p[0] for p in session.env.cr.fetchall()]


def update_products_history(session, product_ids):
    product_obj = session.env['product.product']
    product_history_obj = session.env['product.history']
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
                    session.env.cr.execute(sql, params)
                    stock_moves = session.env.cr.fetchall()
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


def product_history_update_background(cr):
    session = ConnectorSession(cr, SUPERUSER_ID)
    product_ids = get_products(session)
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
    update_products_history(session, product_ids)
