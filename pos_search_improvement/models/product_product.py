# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    multi_barcode_ids = fields.One2many(
        "product.multi.barcode",
        "product_tmpl_id",
        string="Product Multiple Barcodes",
    )

class ProductProduct(models.Model):
    _inherit = "product.product"

    multi_barcode_ids = fields.One2many(
        "product.multi.barcode",
        "product_id",
        string="Product Multiple Barcodes",
    )

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        new_args = self.get_domain_multi_barcode_for_product(args)
        return super(ProductProduct, self).search(
            new_args, offset, limit, order, count=count
        )

    @api.model
    def get_domain_multi_barcode_for_product(self, args):
        """
            Get Multi Barcode for product if when search product with "barcode"
        """
        new_args = []
        for arg in args:
            if arg[0] == "barcode":
                new_args += [
                    "|",
                    ("multi_barcode_ids.barcode", arg[1], arg[2]),
                    arg,
                ]
            else:
                new_args += [arg]
        return new_args
