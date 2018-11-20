# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from datetime import datetime # Used when eval python codes !!

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _get_supplier_code_or_ean(self, seller_id):
        """
        """
        self.ensure_one()
        code, origin_code = '', ''
        seller_line = self.seller_ids.filtered(lambda l: l.name==seller_id and l.product_code)
        if seller_line and seller_line[0].product_code:
            code = seller_line[0].product_code
            origin_code = 'supplier'
        elif self.barcode:
            code = self.barcode
            origin_code = 'barcode'
        if not code:
            raise ValidationError(_("No code for this product %s!") % self.name)
        return code, origin_code



