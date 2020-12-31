# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tools.image

from odoo import api, fields, models
from odoo.tools.image import image_get_resized_images
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"
    image_badge = fields.Binary("Badge-sized image", attachment=True,
        help="Badge-sized image of this contact. It is automatically "\
             "resized as a 315x417px image, with aspect ratio preserved. "\
             "Use this field in badge printing.")

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
        "Badge To Print", default=_get_default_badge_to_print)
    updated_badges_info = fields.Boolean(
        "Updated Badges Information",
        compute="_compute_updated_badges_info",
        store=True)

    # ######### COMPUTE FUNCTIONS ############

    @api.depends('badge_to_print', 'is_member', 'is_associated_people')
    def _compute_updated_badges_info(self):
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
            # Update Badge Image
            if partner_vals.get('image'):
                partner_vals.update({
                    'image_badge': self.get_badge_image(partner_vals['image'])
                })
            for field_name in fields_trigger_badge_reprint:
                if field_name in partner_vals and \
                        partner_vals.get(field_name) != partner[field_name]:
                    partner_vals['badge_to_print'] = True
                    break
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

    @api.model
    def create(self, vals):
        # Update Badge Image
        if vals.get('image'):
            vals.update({
                'image_badge': self.get_badge_image(vals['image'])
            })
        res = super(ResPartner, self).create(vals)
        return res

    @api.model
    def get_badge_image(self, src_image):
        medium_name='image_badge'
        sizes={
            medium_name: (315, 417)
        }
        vals = image_get_resized_images(
            src_image, return_small=False, medium_name=medium_name,
            sizes=sizes)
        return vals.get(medium_name)
