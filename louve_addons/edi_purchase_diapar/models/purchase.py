# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from datetime import datetime # Used when eval python codes !!

from openerp import models, api, fields, _, tools
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _consolidate_products(self):
        """
            Consolidate order lines by product.
            Raise if Tax or price different.
            @return: dict {product_id(record):[code_or_ean, qty, price, taxes(records)]}
        """
        self.ensure_one()
        if not self.order_line:
            raise ValidationError(_("No lines in this order %s!") % self.name)
        lines = {}
        for line in self.order_line:
            if line.product_id in lines:
                if line.taxes_id != lines[line.product_id]['taxes_id']:
                    raise ValidationError(_("Check taxes for lines with product %s!") % line.product_id.name)
                if line.price_unit != lines[line.product_id]['price_unit']:
                    raise ValidationError(_("Check price for lines with product %s!") % line.product_id.name)
                lines[line.product_id]['quantity'] += line.product_qty
            else:
                code, origin_code = line.product_id._get_supplier_code_or_ean(line.partner_id)
                values = {
                    'code': code,
                    'origin_code': origin_code,
                    'quantity': line.product_qty_package,
                    'price_unit': line.price_unit,
                    'taxes_id': line.taxes_id
                }
                lines.update({line.product_id: values})
        return lines


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    partner_is_edi = fields.Boolean(related='partner_id.is_edi', string='Partner (Is Edit)', store=True)
