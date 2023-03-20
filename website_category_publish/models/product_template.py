# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_categ_published = fields.Boolean(
        'Is Categ published',
        store=True,
        compute="_compute_is_categ_published"
    )

    @api.depends("public_categ_ids", "public_categ_ids.is_published")
    def _compute_is_categ_published(self):
        for pt in self:
            is_published = True
            if pt.public_categ_ids:
                is_published = any(c.is_published for c in pt.public_categ_ids)
            pt.is_categ_published = is_published
