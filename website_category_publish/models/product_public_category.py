# Copyright 2020 Tecnativa - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    @api.multi
    def write(self, vals):
        res = super(ProductPublicCategory, self).write(vals)
        if "website_published" in vals:
            for categ in self:
                childs = categ.child_id.filtered(
                    lambda c: c.website_published != categ.website_published)
                childs.write({'website_published': categ.website_published})
        return res
