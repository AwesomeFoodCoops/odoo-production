# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PricetagModel(models.Model):
    _name = 'pricetag.model'
    _description = "Pricetag Model"

    name = fields.Char(required=True)
    pricetag_paperformat_id = fields.Many2one(
        'report.paperformat',
        string='Paper Format',
        required=True
    )
    report_model = fields.Char(
        string='ID of the report template',
        required=True
    )
