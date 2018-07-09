# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, fields


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'
    _order = "inventory_id, location_name, product_name, product_code, prodlot_name"
