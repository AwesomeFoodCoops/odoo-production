# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)

from odoo import api, models


class ReportPricetag(models.AbstractModel):
    _name = "report.product_print_category.report_pricetag"

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'product_print_category.report_pricetag'
        )
        return self._prepare_categories_data(data)

    @api.model
    def _prepare_categories_data(self, data):
        category_obj = self.env["product.print.category"]
        line_obj = self.env["product.print.wizard.line"]
        # ordering data to print
        lines_dict = {}
        for line_id in data["line_data"]:
            line = line_obj.browse(int(line_id))
            category = line.product_id.print_category_id
            if category.id not in lines_dict:
                lines_dict[category.id] = [line.id]
            else:
                lines_dict[category.id].append(line.id)
        # Computing data to transfer
        categories_data = []
        for category_id, line_ids in lines_dict.items():
            category = category_obj.browse(category_id)
            categories_data.append({
                "print_category": category,
                "report_model": "report_pricetag_custom",
                "lines": line_obj.browse(line_ids),
            })
        return {'categories_data': categories_data}
