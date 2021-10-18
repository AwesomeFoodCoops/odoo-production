# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, api, fields


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    week_number = fields.Integer(
        string='Week Number',
        related="order_id.week_number",
        store=True
    )
    week_name = fields.Char(
        string='Week',
        related='order_id.week_name',
        store=True,
    )
    week_day = fields.Char(
        string="Day",
        related="order_id.week_day",
        store=True,
    )
    cycle = fields.Char(
        string="Cycle",
        related="order_id.cycle",
        store=True,
    )
    order_id = fields.Many2one(index=True)
    product_id = fields.Many2one(index=True)

    product_default_code = fields.Char(
        string="Internal Reference",
        related="product_id.default_code",
        store=True
    )

    @api.multi
    def compute_amount_line_all(self):
        """
        Util function that easily call _compute_amount_line_all from JSONRPC
        """
        self._compute_amount_line_all()
        return True
