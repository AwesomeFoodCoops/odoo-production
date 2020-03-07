# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models, api, _
from odoo.exceptions import ValidationError


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.constrains("product_code")
    def _check_product_code(self):
        if self.product_code:
            if not self.product_code.isdigit():
                raise ValidationError(
                    _("Product code must be numeric for %s!") % self.name.name
                )
            if len(self.product_code) != 6:
                raise ValidationError(
                    _("Product code must be 6 digits for %s!") % self.name.name
                )
