#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)

from odoo import api, models


class ProductPrintWizard(models.TransientModel):
    _inherit = "product.print.wizard"

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = self._prepare_data()
        report_name = 'product_print_category.pricetag'
        if self.line_ids:
            reportname = self.line_ids[0].print_category_id.\
                pricetag_model_id.report_model
            if reportname == 'coop_default_pricetag.report_pricetag_barcode':
                report_name = 'coop_default_pricetag.pricetag_barcode'
        return self.env.ref(report_name).report_action(
            self, data=data)
