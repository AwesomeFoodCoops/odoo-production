# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    department_id = fields.Many2one(
        string="Origin Department",
        comodel_name="res.country.department",
        help="Department of production of the product",
    )

    @api.depends("origin_description", "country_id")
    @api.multi
    def _compute_pricetag_origin(self):
        for data in self:
            tmp = ""
            if data.origin_description:
                tmp = data.origin_description
            if data.department_id:
                tmp = data.department_id.name + \
                    (" - " + tmp if tmp else "")
            if data.country_id:
                tmp = data.country_id.name.upper() + \
                    (" - " + tmp if tmp else "")
            if data.maker_description:
                tmp = (tmp and (tmp + " - ") or "") + data.maker_description
            data.pricetag_origin = tmp

        # Constraints section
    @api.multi
    @api.constrains("department_id", "country_id")
    def _check_origin_department_country(self):
        for data in self:
            if data.department_id.country_id and \
               data.department_id.country_id.id != data.country_id.id:
                raise UserError(
                    _("Error ! Department %s doesn't belong to %s.")
                    % (data.department_id.name, data.country_id.name)
                )

    # Views section
    @api.multi
    @api.onchange("department_id")
    def onchange_department_id(self):
        for data in self:
            if data.department_id:
                data.country_id = data.department_id.country_id
            else:
                data.country_id = False

#     @api.multi
    @api.onchange("country_id")
    def onchange_country_id(self):
        for data in self:
            if data.country_id:
                data.department_id = False
