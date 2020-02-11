# -*- coding: utf-8 -*-
##############################################################################
#
#    Sale - Food Module for Odoo
#    Copyright (C) 2012-Today GRAP (http://www.grap.coop)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import tools, fields, models, api


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

