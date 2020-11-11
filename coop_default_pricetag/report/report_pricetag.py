# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ReportPricetagBase(models.AbstractModel):
    _name = "report.coop_default_pricetag.report_pricetag_base"
    _description = "Pricetag Report"

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
        line_ids = data.get('line_data')
        report_context = self._context.copy()
        report_context.update(data.get("used_context", {}))
        product_res = self.with_context(report_context)._get_products(
            line_ids
        )
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


class ReportPricetagVegetables(models.AbstractModel):
    _name = 'report.coop_default_pricetag.report_pricetag_vegetables'
    _inherit = 'report.coop_default_pricetag.report_pricetag'


class ReportPricetagSimpleBarcode(models.AbstractModel):
    _name = 'report.coop_default_pricetag.report_pricetag_simple_barcode'
    _inherit = 'report.coop_default_pricetag.report_pricetag_base'
