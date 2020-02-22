# -*- coding: utf-8 -*-


from openerp import api
from openerp import tools
from openerp.osv import fields, osv


class stock_inventory(osv.osv):
    _inherit = 'stock.inventory'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_history')
        cr.execute("""
            CREATE OR REPLACE VIEW stock_history AS (
              SELECT MIN(id) as id,
                move_id,
                location_id,
                company_id,
                product_id,
                product_categ_id,
                product_template_id,
                SUM(quantity) as quantity,
                date,
                COALESCE(SUM(price_unit_on_quant * quantity) /
                NULLIF(SUM(quantity), 0), 0) as price_unit_on_quant,
                source,
                string_agg(DISTINCT serial_number, ', ' ORDER BY
                serial_number) AS serial_number
                FROM
                ((SELECT
                    stock_move.id AS id,
                    stock_move.id AS move_id,
                    dest_location.id AS location_id,
                    dest_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.id AS product_template_id,
                    product_template.categ_id AS product_categ_id,
                    quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_production_lot.name AS serial_number
                FROM
                    stock_quant as quant
                JOIN
                    stock_quant_move_rel ON
                    stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON
                    stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN
                    stock_production_lot ON
                    stock_production_lot.id = quant.lot_id
                JOIN
                    stock_location dest_location ON
                    stock_move.location_dest_id = dest_location.id
                JOIN
                    stock_location source_location ON
                    stock_move.location_id = source_location.id
                JOIN
                    product_product ON
                    product_product.id = stock_move.product_id
                JOIN
                    product_template ON
                    product_template.id = product_product.product_tmpl_id
                WHERE product_template.type != 'consu' AND quant.qty>0 AND
                stock_move.state = 'done' AND
                dest_location.usage in ('internal', 'transit')
                AND (
                    not (source_location.company_id is null and
                    dest_location.company_id is null) or
                    source_location.company_id != dest_location.company_id or
                    source_location.usage not in ('internal', 'transit'))
                ) UNION ALL
                (SELECT
                    (-1) * stock_move.id AS id,
                    stock_move.id AS move_id,
                    source_location.id AS location_id,
                    source_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.id AS product_template_id,
                    product_template.categ_id AS product_categ_id,
                    - quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_production_lot.name AS serial_number
                FROM
                    stock_quant as quant
                JOIN
                    stock_quant_move_rel ON
                    stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN
                    stock_production_lot ON
                    stock_production_lot.id = quant.lot_id
                JOIN
                    stock_location source_location ON
                    stock_move.location_id = source_location.id
                JOIN
                    stock_location dest_location ON
                    stock_move.location_dest_id = dest_location.id
                JOIN
                    product_product ON
                    product_product.id = stock_move.product_id
                JOIN
                    product_template ON
                    product_template.id = product_product.product_tmpl_id
                WHERE product_template.type != 'consu' AND quant.qty>0 AND
                stock_move.state = 'done' AND
                source_location.usage in ('internal', 'transit')
                AND (
                    not (dest_location.company_id is null and
                    source_location.company_id is null) or
                    dest_location.company_id != source_location.company_id or
                    dest_location.usage not in ('internal', 'transit'))
                ))
                AS foo
                GROUP BY
                move_id, location_id, company_id, product_id,
                product_categ_id, date, source, product_template_id
            )""")
    

    def post_inventory(self, cr, uid, inv, context=None):
        res = super(stock_inventory, self).post_inventory(
            cr, uid, inv, context=context)
        if inv:
            move_obj = self.pool.get('stock.move')
            date_inv = inv.date
            move_ids = inv.move_ids.ids
            move_obj.write(cr, uid, move_ids, {'date': date_inv},
                           context=context)
        return res
