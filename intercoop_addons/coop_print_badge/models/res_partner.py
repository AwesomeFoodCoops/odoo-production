# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.tools.image
from openerp import api, fields, models
from openerp.tools.image import image_resize_image
from openerp.tools.safe_eval import safe_eval

def new_image_resize_image_medium(
        base64_source, size=(315, 417), encoding='base64', filetype=None,
        avoid_if_small=False):
    return image_resize_image(
        base64_source, size, encoding, filetype, avoid_if_small)


# Override native method
openerp.tools.image.image_resize_image_medium = new_image_resize_image_medium


class ResPartner(models.Model):
    _inherit = "res.partner"

    # ### FUNCTIONS FOR DEFINING DEFAULT VALUES #########

    @api.model
    def _get_default_badge_to_print(self):
        trigger_fields = self._get_field_names_trigger_badge_reprint()
        fields_has_value = trigger_fields and \
            all([self[field_item] for field_item in trigger_fields]) or \
            False
        return fields_has_value

    # ########## FIELDS DEFINITION ############

    badge_to_print = fields.Boolean(
        "Badge To Print",
        default=_get_default_badge_to_print)

    updated_badges_info = fields.Boolean(
        'Updated Badges Information',
        compute="_computed_updated_badges_info",
        store=True)

    # ######### COMPUTE FUNCTIONS ############

    @api.depends('badge_to_print', 'is_member', 'is_associated_people')
    def _computed_updated_badges_info(self):
        '''
        @Function to compute the value of field updated_badges_info
        '''
        for record in self:
            if record.badge_to_print and \
               (record.is_member or record.is_associated_people):
                record.updated_badges_info = True
            else:
                record.updated_badges_info = False

    # ###### RECORD OPERATION FUNCTIONS #########
    @api.multi
    def untick_badges_to_print(self):
        for record in self:
            record.badge_to_print = False

    @api.multi
    def write(self, vals):
        res = False
        fields_trigger_badge_reprint = \
            self.env['res.partner']._get_field_names_trigger_badge_reprint()
        for partner in self:
            partner_vals = vals.copy()
            for field_name in fields_trigger_badge_reprint:
                if field_name in partner_vals and \
                        partner_vals.get(field_name) != partner[field_name]:
                    partner_vals['badge_to_print'] = True
                    break
            if partner_vals.get('badge_to_print') and \
                    not partner._check_badge_to_print(vals):
                partner_vals['badge_to_print'] = False
            res = super(ResPartner, partner).write(partner_vals)

        return res

    # ######## SUPPORTING FUNCTIONS ##########

    @api.model
    def _get_field_names_trigger_badge_reprint(self):
        '''
        @Function to get a list of fields in Partner object which triggers
        badge to print
        '''
        field_str = self.env['ir.config_parameter'].sudo().get_param(
            'reprint_change_field_ids', '[]')
        field_ids = safe_eval(field_str)
        fields_recs = self.env['ir.model.fields'].sudo().browse(field_ids)
        return [field_item.name for field_item in fields_recs]

    @api.multi
    def _check_badge_to_print(self, vals={}):
        self.ensure_one()
        trigger_fields = self._get_field_names_trigger_badge_reprint()
        fields_has_value = trigger_fields and \
            all([field_item in vals and vals[field_item] or self[field_item]
                for field_item in trigger_fields]) or False
        #  S#25849: make sure the image is not the default one
        img_field = 'image'
        if img_field in trigger_fields and fields_has_value:
            default_img = self._get_default_image(False)
            if img_field in vals:
                partner_img = vals[img_field]
            else:
                partner_img = self[img_field]
            if not partner_img or default_img == partner_img:
                return False
        return fields_has_value

    @api.model
    def _get_default_image(self, is_company, colorize=False):
        colorize = False
        return super(ResPartner, self)._get_default_image(is_company, colorize)

