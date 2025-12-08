# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = [_name, "utm.mixin"]

    utm_source_ids = fields.Many2many(
        "utm.source",
        string="Discovery Meeting Sources"
    )
