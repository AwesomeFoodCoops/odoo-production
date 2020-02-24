# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    _order = (
        "inventory_id, location_id, product_id, prod_lot_id"
    )
