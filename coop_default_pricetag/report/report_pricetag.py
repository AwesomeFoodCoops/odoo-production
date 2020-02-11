# -*- encoding: utf-8 -*-

from odoo import api, models


class ReportPricetagBase(models.AbstractModel):
    _name = "report.coop_default_pricetag.report_pricetag_base"

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.render_html(data)

    @api.model
    def _get_products(self, lines):
        result = []
        line_ids = self.env["product.print.wizard.line"].browse(lines)
        for line in line_ids:
            val = {}
            val["line"] = line
            val["product"] = line.product_id
            result.append(val)
        return result

    @api.multi
    def render_html(self, data):
        self.model = self.env.context.get("active_model")
        docs = self.env[self.model].browse(self.env.context.get("active_id"))
        line_ids = data.get('line_data')
        report_context = self._context.copy()
        report_context.update(data.get("used_context", {}))
        product_res = self.with_context(report_context)._get_products(
            line_ids
        )
        if line_ids:
            categ_ids = self.env["product.print.wizard.line"].browse(
                line_ids)[0].print_category_id.pricetag_model_id
        docargs = {
            "partner_id": self.env.user.partner_id,
            "Products": product_res,
        }
        return docargs


class ReportPricetag(models.AbstractModel):
    _name = "report.coop_default_pricetag.report_pricetag"
    _inherit = "report.coop_default_pricetag.report_pricetag_base"


class ReportPricetagBarcode(models.AbstractModel):
    _name = "report.coop_default_pricetag.report_pricetag_barcode"
    _inherit = "report.coop_default_pricetag.report_pricetag_base"
