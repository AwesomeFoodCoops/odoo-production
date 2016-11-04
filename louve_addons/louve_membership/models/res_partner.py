# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _

from openerp.exceptions import ValidationError

EXTRA_COOPERATIVE_STATE_SELECTION = [
    ('not_concerned', 'Not Concerned'),
    ('up_to_date', 'Up to date'),
    ('alert', 'Alert'),
    ('suspended', 'Suspended'),
    ('delay', 'Delay'),
    ('blocked', 'Blocked'),
    ('unpayed', 'Unpayed'),
    ('unsubscribed', 'Unsubscribed'),
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    COOPERATIVE_STATE_CUSTOMER = ['up_to_date', 'alert', 'delay']

    # Compute Section
    @api.multi
    @api.depends('fundraising_partner_type_ids')
    def _compute_is_underclass_population(self):
        xml_id = self.env.ref('louve_membership.underclass_population_type').id
        for partner in self:
            partner.is_underclass_population =\
                xml_id in partner.fundraising_partner_type_ids.ids

    # New Column Section
    is_louve_member = fields.Boolean('Is Louve Member')

    is_associated_people = fields.Boolean('Is Associated People')

    is_unpayed = fields.Boolean(
        string='Unpayed', help="Check this box, if the partner has late"
        " payments for him capital subscriptions. this will prevent him"
        " to buy.")

    is_unsubscribed = fields.Boolean(
        string='Unsubscribed', help="Check this box, if the partner left the"
        " the cooperative. this will prevent him to buy.")

    adult_number_home = fields.Integer('Number of Adult in the Home')

    sex = fields.Char('Sex')

    old_coop_number = fields.Char('Civi CRM Old Number')

    is_underclass_population = fields.Boolean(
        'is Underclass Population', compute=_compute_is_underclass_population)

    contact_origin_id = fields.Many2one(
        comodel_name='res.contact.origin', string='Contact Origin')

    is_deceased = fields.Boolean(string='Is Deceased')

    is_type_A_capital_subscriptor = fields.Boolean(
        'Has a type A capital subscription', store=True,
        compute="_compute_is_type_A_capital_subscriptor")

    # Important : Overloaded Field Section
    customer = fields.Boolean(
        compute='_compute_customer', store=True, readonly=True)

    # Note we use selection instead of selection_add, to have a correct
    # order in the status widget
    cooperative_state = fields.Selection(
        selection=EXTRA_COOPERATIVE_STATE_SELECTION)

    # Compute Section
    @api.multi
    @api.depends(
        'invoice_ids.fundraising_category_id.is_part_A',
        'invoice_ids.fundraising_category_id', 'invoice_ids.state')
    def _compute_is_type_A_capital_subscriptor(self):
        category_obj = self.env['capital.fundraising.category']
        A_categories = category_obj.search([('is_part_A', '=', True)])
        for partner in self:
            invoice_obj = self.env['account.invoice']
            invoices = invoice_obj.search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['open', 'paid']),
                ('fundraising_category_id', 'in', A_categories.ids)])
            partner.is_type_A_capital_subscriptor = len(invoices)

    @api.depends(
        'working_state', 'is_unpayed', 'is_unsubscribed',
        'is_type_A_capital_subscriptor', 'is_associated_people',
        'parent_id.cooperative_state')
    @api.multi
    def _compute_cooperative_state(self):
        for partner in self:
            if partner.is_associated_people:
                # Associated People
                partner.cooperative_state = partner.parent_id.cooperative_state
            elif partner.is_type_A_capital_subscriptor:
                # Type A Subscriptor
                    if partner.is_unsubscribed:
                        partner.cooperative_state = 'unsubscribed'
                    elif partner.is_unpayed:
                        partner.cooperative_state = 'unpayed'
                    else:
                        partner.cooperative_state = partner.working_state
            else:
                partner.cooperative_state = 'not_concerned'

    @api.depends('cooperative_state')
    @api.multi
    def _compute_customer(self):
        for partner in self:
            partner.customer =\
                partner.cooperative_state in self.COOPERATIVE_STATE_CUSTOMER

    # Overload Section
    @api.model
    def create(self, vals):
        generate_barcode = False
        barcode_rule_obj = self.env['barcode.rule']

        if vals.get('is_louve_member', False):
            # Affect a default member type
            xml_id = self.env.ref('louve_membership.default_member_type').id
            vals.get('fundraising_partner_type_ids', []).append((4, xml_id))

        if vals.get('parent_id', False):
            parent_partner = self.browse(vals.get('parent_id', False))
            if parent_partner.is_louve_member:
                if not parent_partner.is_type_A_capital_subscriptor:
                    raise ValidationError(_(
                        "You can not associate a people to that person"
                        " because he didn't subscribed A part."))
                # Set associated People
                vals['is_associated_people'] = True

                # Generate Associated Barcode
                barcode_rule_id = barcode_rule_obj.search(
                    [('for_associated_people', '=', True)], limit=1)
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
