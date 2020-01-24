# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardValuationHistory(models.TransientModel):

    _inherit = 'wizard.valuation.history'

    @api.multi
    def export_xlsx(self):
        self.ensure_one()
        fmt_datetime = "%d/%m/%Y %H:%M:%S"
        user_tz = self._context.get('tz', self.env.user.tz) or 'UTC'
        self_with_ctx = self.with_context(tz=user_tz)
        inventory_dt = fields.Datetime.context_timestamp(
            self_with_ctx, fields.Datetime.from_string(self.date)
        )
        today_dt = fields.Datetime.context_timestamp(
            self_with_ctx, fields.Datetime.from_string(fields.Datetime.now())
        )
        inventory_dt_str = inventory_dt.strftime(fmt_datetime)
        today_dt_str = today_dt.strftime(fmt_datetime)

        datas = dict()
        res = self.env['report'].get_action(self, "stock_inventory_xlsx")
        datas['context'] = self._context
        datas['history_values_lst'] = self.get_history_datas()
        datas['inventory_date'] = inventory_dt_str
        datas['print_date'] = today_dt_str
        res.update({
            'datas': datas,
        })
        return res

    @api.multi
    def get_history_datas(self):
        self.ensure_one()
        history_values_lst = []
        date_str = self.date or fields.Datetime.now()

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
        JOIN product_product product
            ON stock_move.product_id = product.id
        WHERE  quant.qty > 0
            AND product.active IS TRUE
            AND stock_move.state = 'done'
            AND dest_location.usage IN ( 'internal', 'transit' )
            AND ( NOT ( source_location.company_id IS NULL
                        AND dest_location.company_id IS NULL )
                    OR source_location.company_id != dest_location.company_id
                    OR source_location.usage NOT IN ( 'internal', 'transit' )
                )
            AND stock_move.date <= %s
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
        JOIN product_product product
            ON stock_move.product_id = product.id
        WHERE  quant.qty > 0
            AND product.active IS TRUE
            AND stock_move.state = 'done'
            AND source_location.usage IN ( 'internal', 'transit' )
            AND ( NOT ( dest_location.company_id IS NULL
                        AND source_location.company_id IS NULL )
                    OR dest_location.company_id != source_location.company_id
                    OR dest_location.usage NOT IN ( 'internal', 'transit' ) 
                )
            AND stock_move.date <= %s
        GROUP  BY stock_move.product_id
    )
) AS foo
GROUP  BY product_id

"""

        self.env.cr.execute(query, (date_str, date_str))
        history_datas = self.env.cr.fetchall()
        for history in history_datas:
            product_id = int(history[0])
            product_obj = self.env['product.product'].browse(product_id)
            history_values_lst.append({
                'internal_ref': product_obj.default_code or '',
                'barcode': product_obj.barcode or '',
                'name': product_obj.name,
                'quantity': history[1],
                'standard_price': product_obj.standard_price,
            })

        return history_values_lst
