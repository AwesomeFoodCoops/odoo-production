# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class UtmSourceCategory(models.Model):
    _name = "utm.source.category"
    _description = "UTM Source Category"

    name = fields.Char(required=1)
    source_ids = fields.One2many(
        "utm.source",
        "category_id"
    )
