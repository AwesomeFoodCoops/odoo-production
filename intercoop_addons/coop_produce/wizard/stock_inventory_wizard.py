# -*- coding: utf-8 -*-

from openerp import api, fields, models


class StockInventoryWizard(models.TransientModel):
    _name = 'stock.inventory.wizard'

    week_date = fields.Date(
        string="Began order scheduling on.",
        required=True,
        help="Week planning start date"
    )

    @api.multi
    def action_ok(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        if active_id:
            current_stock_inv = self.env['stock.inventory'].browse(active_id)
            current_stock_inv.write({'week_date': self.week_date})
            return current_stock_inv.action_done()
        return True
