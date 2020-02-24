# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models, api


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    vendor_product_code = fields.Char(
        compute="_compute_product_code"
    )

    @api.multi
    def _compute_product_code(self):
        for pack in self:
            sellers = pack.product_id.seller_ids
            for seller in sellers:
                if seller.name == pack.picking_id.partner_id:
                    pack.vendor_product_code = seller.product_code
