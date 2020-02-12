# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import tools, fields, models, api


class ProductLabel(models.Model):
    _name = "product.label"

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one(string="Company", comodel_name="res.company")
    website = fields.Char(string="Website")
    note = fields.Text(string="Note")
    image = fields.Binary(
        string="Image",
        attachment=True,
        help="This field holds the image"
        " used as image for the label, limited to 1024x1024px.",
    )
    image_medium = fields.Binary(
        string="Medium-sized image",
        attachment=True,
        help="Medium-sized"
        " image of the product. It is automatically resized as a 128x128px"
        " image, with aspect ratio preserved, only when the image exceeds one"
        " of those sizes. Use this field in form views or some kanban views.",
    )
    image_small = fields.Binary(
        string="Small-sized image",
        attachment=True,
        help="Small-sized image"
        " of the product. It is automatically resized as a 64x64px image,"
        " with aspect ratio preserved. Use this field anywhere a small image"
        " is required.",
    )

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(ProductLabel, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(ProductLabel, self).write(vals)
