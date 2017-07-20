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
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        im2 = im.crop(bbox)
    else:
        im2 = im
    # new size in pixel, ratio : 1 pixel = 0.264583333 mm
    new_size = (int(37 / 0.264583333), int(47 / 0.264583333))
    im2 = im2.resize(new_size, Image.ANTIALIAS)
    buffer = cStringIO.StringIO()
    im2.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue())


class ReportPrintbadge(models.AbstractModel):
    _name = 'report.coop_print_badge.report_printbadge'

    @api.multi
    def render_html(self, data):
        res_partner_env = self.env['res.partner']
        partners = res_partner_env.search([('id', 'in', self.ids)])
        images = {}
        default_im = res_partner_env._get_default_image(False, True)
        for rec in partners:
            im = Image.open(BytesIO(base64.b64decode(rec.image or default_im)))
            images.update({rec.id: trim_image(im)})

        docargs = {
            'doc_ids': self.ids,
            'partner_id': self.env.user.partner_id,
            'doc_model': 'res.partner',
            'partners': partners,
            'images': images
        }
        return self.env['report'].render(
            'coop_print_badge.report_printbadge', docargs)
