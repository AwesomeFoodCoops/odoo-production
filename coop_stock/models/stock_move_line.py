# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    vendor_product_code = fields.Char(
        compute="_compute_product_code"
    )
    product_default_code = fields.Char(
        string="Internal Reference",
        related="product_id.default_code"
    )
    picking_id = fields.Many2one(index=True)
    result_package_id = fields.Many2one(index=True)

    @api.multi
    def _compute_product_code(self):
        for move_line in self:
            sellers = move_line.product_id.seller_ids
            for seller in sellers:
                if seller.name == move_line.picking_id.partner_id:
                    move_line.vendor_product_code = seller.product_code
