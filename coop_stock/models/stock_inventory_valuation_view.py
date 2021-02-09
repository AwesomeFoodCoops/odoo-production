# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockInventoryValuationView(models.TransientModel):
    _inherit = 'stock.inventory.valuation.view'

    categ_name = fields.Char()


class StockInventoryValuationReport(models.TransientModel):
    _inherit = 'report.stock.inventory.valuation.report'

    @api.multi
    def _compute_results(self):
        '''
        Override this function to add the category name
        '''
        self.ensure_one()
        if not self.compute_at_date:
            self.date = fields.Datetime.now()
        products = self.env['product.product'].\
            search([('type', '=', 'product')]).\
            with_context(dict(to_date=self.date, company_owned=True,
                              create=False, edit=False))
        ReportLine = self.env['stock.inventory.valuation.view']
        for product in products:
            standard_price = product.standard_price
            if self.compute_at_date:
                standard_price = product.get_history_price(
                    self.env.user.company_id.id,
                    date=self.date)
            line = {
                'name': product.name,
                'reference': product.default_code,
                'barcode': product.barcode,
                'qty_at_date': product.qty_at_date,
                'uom_id': product.uom_id,
                'currency_id': product.currency_id,
                'cost_currency_id': product.cost_currency_id,
                'standard_price': standard_price,
                'stock_value': product.qty_at_date * standard_price,
                'cost_method': product.cost_method,
                'categ_name': product.categ_id.name
            }
            self.results += ReportLine.new(line)
