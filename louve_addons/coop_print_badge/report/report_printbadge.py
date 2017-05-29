# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from io import BytesIO
from PIL import Image, ImageChops
import base64
import cStringIO

def trim_image(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        im2 = im.crop(bbox)
    else:
        im2= null
    buffer = cStringIO.StringIO()
    im2.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue())

class ReportPrintbadge(models.AbstractModel):
    _name = 'report.coop_print_badge.report_printbadge'

    @api.multi
    def render_html(self, data):
        partners = self.env['res.partner'].browse(self.ids)
        for p in partners :
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>", p['image']
            im = Image.open(BytesIO(base64.b64decode(p['image'])))
            p['image']=trim_image(im)

        docargs = {
            'doc_ids': self.ids,
            'partner_id': self.env.user.partner_id,
            'doc_model': 'res.partner',
            'partners': partners,
        }
        return self.env['report'].render(
            'coop_print_badge.report_printbadge', docargs)
