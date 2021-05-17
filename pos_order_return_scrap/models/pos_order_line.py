# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    is_scrap = fields.Boolean(
        string="Is Scrap?",
        copy=False
    )
