# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models, api


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.onchange('product_qty_package')
    def product_qty_package_onchange(self):
        if self.product_qty_package == int(self.product_qty_package):
            self.product_qty = self.product_qty_package * self.package_qty
