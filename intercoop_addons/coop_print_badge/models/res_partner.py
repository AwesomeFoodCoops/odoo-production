# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_default_badge_to_print(self):
        return self.name and self.barcode_base and self.image

    badge_to_print = fields.Boolean("Badge To Print",
                                    default=_get_default_badge_to_print)
    updated_badges_info = fields.Boolean('Updated Badges Information',
                                         compute="_computed_updated_badges_info")

    @api.multi
    @api.onchange('image', 'barcode')
    def onchange_badge_to_print(self):
        for record in self:
            if record.image and record.name and record.barcode_base \
               and record.barcode:
                record.badge_to_print = True
            else:
                record.badge_to_print = False

    @api.multi
    @api.depends('badge_to_print')
    def _computed_updated_badges_info(self):
        for record in self:
            if record.badge_to_print and \
               (record.is_member or record.is_associated_people) and \
               record.image and record.name and record.barcode_base:
                record.updated_badges_info = True
            else:
                record.updated_badges_info = False
                record.badge_to_print = False

    @api.multi
    def untick_badges_to_print(self):
        for record in self:
            record.updated_badges_info = False
            record.badge_to_print = False

    @api.multi
    def write(self, vals):
        if vals.get('barcode', False) or vals.get('name', False) or \
           vals.get('image', False):
            vals.update({'badge_to_print': True})
        return super(ResPartner, self).write(vals)
