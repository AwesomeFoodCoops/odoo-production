# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_ref = fields.Char(
        related="purchase_id.partner_ref",
        readonly=True,
    )
