# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import StringIO
import barcode
from barcode.writer import ImageWriter

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('barcode')
    def get_barcode_image(self):
        for partner in self:
            if partner.barcode:
                fp = StringIO.StringIO()
                barcode.generate(
                    'EAN13', partner.barcode,
                    writer=ImageWriter(), output=fp,
                    writer_options={
                        'module_height': 15, 'module_width': 0.4,
                        'font_size': 23, 'text_distance': 2})
                partner.barcode_image = base64.b64encode(fp.getvalue())
            else:
                partner.barcode_image = False

    barcode_image = fields.Binary(
        string='Image of the barcode', compute='get_barcode_image', store=True)
