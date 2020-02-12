# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
