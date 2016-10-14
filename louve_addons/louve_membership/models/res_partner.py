# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Compute Section
    @api.multi
    @api.depends('fundraising_partner_type_ids')
    def _compute_is_underclass_population(self):
        xml_id = self.env.ref('louve_membership.underclass_population_type').id
        for partner in self:
            partner.is_underclass_population =\
                xml_id in partner.fundraising_partner_type_ids.ids

    # Column Section
    is_louve_member = fields.Boolean('Is Louve Member')

    is_associated_people = fields.Boolean('Is Associated People')

    adult_number_home = fields.Integer('Number of Adult in the Home')

    sex = fields.Char('Sex')

    old_coop_number = fields.Char('Civi CRM Old Number')

    is_underclass_population = fields.Boolean(
        'is Underclass Population', compute=_compute_is_underclass_population)

    contact_origin_id = fields.Many2one(
        comodel_name='res.contact.origin', string='Contact Origin')

    is_deceased = fields.Boolean(string='Is Deceased')

    @api.depends('parent_id.is_louve_member', 'is_associated_people')
    @api.multi
    def make_associated_people(self):
        # TODO FIXME
        for partner in self:
            if partner.is_associated_people and partner.parent_id:
                partner.is_louve_member = partner.parent_id.is_louve_member
                partner.customer = partner.parent_id.customer
                partner.cooperative_state = partner.parent_id.cooperative_state

    @api.depends(
        'is_blocked', 'is_unpayed', 'final_standard_point', 'final_ftop_point',
        'shift_type', 'date_alert_stop', 'date_delay_stop')
    @api.multi
    def compute_cooperative_state(self):
        # TODO TEST
        for partner in self:
            if partner.is_associated_people and partner.parent_id:
                partner.cooperative_state = partner.parent_id.cooperative_state
            else:
                partner.cooperative_state =\
                    super(ResPartner, partner).compute_cooperative_state()


    # Overload Section
    @api.model
    def create(self, vals):
        generate_barcode = False
        barcode_rule_obj = self.env['barcode.rule']

        if vals.get('is_louve_member', False):
            # Affect a default member type
            xml_id = self.env.ref('louve_membership.default_member_type').id
            vals.get('fundraising_partner_type_ids', []).append((4, xml_id))

            # Add the barcode rule
            barcode_rule_id = barcode_rule_obj.search(
                [('is_louve_member', '=', True)], limit=1)
            if barcode_rule_id:
                vals['barcode_rule_id'] = barcode_rule_id.id
                generate_barcode = True

        if vals.get('parent_id', False):
            parent_partner = self.browse(vals.get('parent_id', False))
            if parent_partner.is_louve_member:
                # Set associated People
                vals['is_associated_people'] = True

                # Generate Associated Barcode
                barcode_rule_id = barcode_rule_obj.search(
                    [('is_associated_people', '=', True)], limit=1)
                if barcode_rule_id:
                    vals['barcode_rule_id'] = barcode_rule_id.id
                    generate_barcode = True

        partner = super(ResPartner, self).create(vals)
        if generate_barcode:
            partner.generate_base_barcode()
        return partner

    # View section
    @api.multi
    def set_underclass_population(self):
        xml_id = self.env.ref('louve_membership.underclass_population_type').id
        for partner in self:
            partner.fundraising_partner_type_ids = [(4, xml_id)]

    @api.multi
    def remove_underclass_population(self):
        xml_id = self.env.ref('louve_membership.underclass_population_type').id
        for partner in self:
            partner.fundraising_partner_type_ids = [(3, xml_id)]
