# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class PricetagModel(models.Model):
    _name = 'pricetag.model'

    name = fields.Char(string='Name', required=True)
    pricetag_paperformat_id = fields.Many2one(
        'report.paperformat',
        string='Paper Format',
        required=True
    )
    report_model = fields.Char(
        string='ID of the report template',
        required=True
    )


class ProductPrintCategory(models.Model):
    _inherit = "product.print.category"

    @api.model
    def _get_default_model(self):
        return self.env['pricetag.model'].search([], limit=1)

    pricetag_model_id = fields.Many2one(
        'pricetag.model',
        string='Pricetag Model',
        default=lambda s: s._get_default_model()
    )
