

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class gross_margin_xlsx_wizard(models.TransientModel):
    _name = "gross.margin.xlsx.wizard"
    _description = "Gross Margin Wizard"

    from_date = fields.Datetime(required=True)
    to_date = fields.Datetime(required=True)
    category_ids = fields.Many2many(
        comodel_name="product.category",
        string="Categories",
        required=True,
    )

    @api.multi
    def export_report(self):
        self.ensure_one()
        datas = dict()
        report_name = 'pos_gross_margin_xlsx.report_gross_margin_xlsx'
        rp = self.env.ref(report_name)
        
        return rp.report_action(self, data=datas)

    @api.multi
    def get_datas(self):
        self.ensure_one()
        datas = []
        from_date = self.from_date
        to_date = self.to_date
        for categ in self.category_ids:
            products = self.env['product.product'].search([
                ('categ_id', '=', categ.id)
            ])
            pre_tax_net_sales = self.get_pre_tax_net_sales(categ, from_date, to_date)
            inventory_value_beginning = self.get_inventory_value(from_date, products)
            inventory_value_ending = self.get_inventory_value(to_date, products)
            net_purchases = self.get_net_purchases(categ, from_date, to_date)
            total_available = inventory_value_beginning + net_purchases
            
            cogs = total_available - inventory_value_ending
            gross_margin = pre_tax_net_sales - cogs
            datas.append({
                "category": categ.name,
                "pre_tax_net_sales": pre_tax_net_sales,
                "inventory_value_beginning": inventory_value_beginning,
                "net_purchases": net_purchases,
                "total_available": total_available,
                "inventory_value_ending": inventory_value_ending,
                "cogs": cogs,
                "gross_margin": gross_margin
            })
        return datas

    @api.multi
    def get_pre_tax_net_sales(self, categ, from_date, to_date):
        datas = self.env['report.pos.order'].search([
            ('product_categ_id', '=', categ.id),
            ('date', '>=', from_date),
            ('date', '<=', to_date)
        ])
        res = datas and sum(datas.mapped("price_wo_tax")) or 0.0
        return res

    @api.multi
    def get_inventory_value(self, date, products):
        prods = products.with_context(to_date=date)
        res = prods and sum(prods.mapped("stock_value")) or 0.0
        return res

    @api.multi
    def get_net_purchases(self, categ, from_date, to_date):
        res = 0.0
        if not categ:
            return res
        from_date_dt = fields.Datetime.context_timestamp(
            self, from_date)
        from_date_str = from_date_dt.strftime(DF)
        to_date_dt = fields.Datetime.context_timestamp(
            self, to_date)
        to_date_str = to_date_dt.strftime(DF)
        sql = """
            SELECT ail.id
            FROM account_invoice_line ail
            JOIN product_product pp ON pp.id = ail.product_id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN account_invoice ai ON ai.id = ail.invoice_id
            WHERE ai.state != 'cancel'
                AND ai.type IN ('in_invoice', 'in_refund')
                AND pt.categ_id = {categ_id}
                AND ai.date_invoice BETWEEN '{from_date}' AND '{to_date}'
        """.format(
            categ_id=categ.id,
            from_date=from_date_str,
            to_date=to_date_str
        )
        self._cr.execute(sql)
        datas = self._cr.fetchall()
        invoice_line_ids = [d[0] for d in datas]
        lines = self.env['account.invoice.line'].browse(invoice_line_ids)
        res = lines and sum(lines.mapped('price_subtotal_signed')) or 0.0
        return res
