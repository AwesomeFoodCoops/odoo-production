# -*- coding: utf-8 -*-
import erppeek
from datetime import date
from datetime import datetime as dt
from datetime import timedelta as td
from dateutil.relativedelta import relativedelta as rd

old_date = date(2015, 1, 1)


def init_openerp(url, login, password, database):
    try:
        openerp = erppeek.Client(url)
        uid = openerp.login(login, password=password, database=database)
        return openerp, uid
    except:
        return False, False


# Enter your server information below
openerp, uid = init_openerp(
    'url e.g.: http://localhost:8069/',
    'login',
    'password',
    'database',
)


def fix_recompute_history_month():
    print "==============================================================="
    print "================= Recomputing Monthly Histories================="
    print "==============================================================="

    history_range = "months"

    now = date.today()
    if history_range == "months":
        delta = rd(months=1)
    elif history_range == "weeks":
        delta = rd(weeks=1)
    else:
        delta = rd(days=1)
    last_dates = {}
    last_qtys = {}
    product_ids = []
    location_ids = openerp.StockLocation.browse([]).read(['usage'])
    location_ids = dict(map(lambda l: (l['id'], l['usage']), location_ids))

    # here, the limit and offset parameters are here to avoid that the script
    # takes too much time. You'll have to launch it several times, and after
    # each time you have to add the number of processed products to the offset
    products = openerp.ProductProduct.browse(
        [], order="id", limit=118, offset=2282)

    i = 0
    for product in products:
        i += 1
        print "===Precompute %s / %s: %s - %s" % (
            i, len(products), product.id, product.name)
        product_ids.append(product.id)
        history_ids = openerp.ProductHistory.browse([
            ('history_range', '=', history_range),
            ('product_id', '=', product.id)], order='to_date DESC', limit=1)
        if history_ids:
            last_record = history_ids[0]
            last_date = last_record and dt.strptime(
                last_record.to_date, "%Y-%m-%d").date() or old_date
            last_qty = last_record and last_record.end_qty or 0
            from_date = last_date + td(days=1)
        else:
            fetch = openerp.StockMove.browse([
                ('product_id', '=', product.id)],
                order='date', limit=1)
            fetch = fetch and fetch[0] or False
            from_date = fetch and dt.strptime(
                fetch.date.split(" ")[0], "%Y-%m-%d").date() or now
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

    stock_moves = openerp.StockMove.browse([
        ('product_id', 'in', product_ids),
        ('date', '>=', dt.strftime(last_date, "%Y-%m-%d")),
        ('state', '!=', 'cancel')])

    location_id = openerp.StockLocation.browse([])[0].id
    stock_moves = [stock_moves[s] for s in range(len(stock_moves) - 1)]
    stock_moves.sort(key=lambda s: s.product_id.id)

    i = 0
    for product_id in product_ids:
        stock_moves_product = []
        i += 1
        print "===Compute %s / %s: %s" % (i, len(products), product_id)

        while len(stock_moves):
            if stock_moves[0].product_id.id == product_id:
                stock_moves_product.append(stock_moves.pop(0))
            else:
                break

        if not stock_moves_product:
            continue

        stock_moves_product.sort(key=lambda s: s.date)
        product = openerp.ProductProduct.browse(product_id)
        from_date = last_dates.get(product_id, old_date)
        last_qty = last_qtys.get(product_id, 0)
        history_id = False

        while from_date + delta <= now:
            stock_moves_product_dates = []
            start_qty = last_qty
            last_date = from_date + delta - td(days=1)
            purchase_qty = sale_qty = loss_qty = 0
            incoming_qty = outgoing_qty = 0

            i_move = 0
            while i_move < len(stock_moves_product):
                if stock_moves_product[i_move].date >=\
                        dt.strftime(from_date, "%Y-%m-%d %H:%M:%S") and\
                        stock_moves_product[i_move].date <=\
                        dt.strftime(last_date, "%Y-%m-%d %H:%M:%S"):
                    stock_moves_product_dates.append(
                        stock_moves_product.pop(i_move))
                else:
                    i_move += 1

            for move in stock_moves_product_dates:
                if move.state == 'done':
                    if move.location_id.usage == 'internal':
                        if move.location_dest_id.usage == 'supplier':
                            purchase_qty -= move.product_qty
                        elif move.location_dest_id.usage == 'customer':
                            sale_qty -= move.product_qty
                        elif move.location_dest_id.usage == 'inventory':
                            loss_qty -= move.product_qty
                    elif move.location_dest_id.usage == 'internal':
                        if move.location_id.usage == 'supplier':
                            purchase_qty += move.product_qty
                        elif move.location_id.usage == 'customer':
                            sale_qty += move.product_qty
                        elif move.location_id.usage == 'inventory':
                            loss_qty += move.product_qty
                else:
                    if move.location_id.usage == 'internal':
                        if move.location_dest_id.usage == 'supplier':
                            incoming_qty -= move.product_qty
                        elif move.location_dest_id.usage == 'customer':
                            outgoing_qty -= move.product_qty
                        elif move.location_dest_id.usage == 'inventory':
                            outgoing_qty -= move.product_qty
                    elif move.location_dest_id.usage == 'internal':
                        if move.location_id.usage == 'supplier':
                            incoming_qty += move.product_qty
                        elif move.location_id.usage == 'customer':
                            outgoing_qty += move.product_qty
                        elif move.location_id.usage == 'inventory':
                            outgoing_qty += move.product_qty

            last_qty = start_qty + purchase_qty + sale_qty + loss_qty

            vals = {
                'product_id': product_id,
                'product_tmpl_id': product.product_tmpl_id.id,
                'location_id': location_id,
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
            history_id = openerp.ProductHistory.create(vals)
            from_date = last_date + td(days=1)

        # The version currently in production doesn't handle these fields yet
        # if history_id:
        #     if history_range == "months":
        #         product.last_history_month = history_id.id
        #     elif history_range == "weeks":
        #         product.last_history_week = history_id.id
        #     else:
        #         product.last_history_day = history_id.id
    print "==============================================================="
    print "============================= Done!============================"
    print "==============================================================="


fix_recompute_history_month()
