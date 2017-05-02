# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Some code from https://www.odoo.com/apps/modules/8.0/birth_date_age/
# Copyright (C) Sythil

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api


EXTRA_COOPERATIVE_STATE_SELECTION = [
    ('not_concerned', 'Not Concerned'),
    ('unsubscribed', 'Unsubscribed'),
    ('exempted', 'Exempted'),
    ('vacation', 'On Vacation'),
    ('up_to_date', 'Up to date'),
    ('alert', 'Alert'),
    ('suspended', 'Suspended'),
    ('delay', 'Delay'),
    ('blocked', 'Blocked'),
    ('unpayed', 'Unpayed'),
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    COOPERATIVE_STATE_CUSTOMER = ['up_to_date', 'alert', 'delay', 'exempted']

    SEX_SELECTION = [
        ('m', 'male'),
        ('f', 'female'),
    ]

    # New Column Section
    is_louve_member = fields.Boolean('Is Louve Member')

    is_unpayed = fields.Boolean(
        string='Unpayed', help="Check this box, if the partner has late"
        " payments for him capital subscriptions. this will prevent him"
        " to buy.")

    is_unsubscribed = fields.Boolean(
        string='Unsubscribed', store=True, help="Computed field."
        " This box is checked if the user is not linked"
        " to a template registration.",
        compute="_compute_is_unsubscribed")

    adult_number_home = fields.Integer('Number of Adult in the Home')

    sex = fields.Selection(
        selection=SEX_SELECTION, string='Sex')

    old_coop_number = fields.Char('Civi CRM Old Number')
    temp_coop_number = fields.Char('Temporary number')

    is_underclass_population = fields.Boolean(
        'is Underclass Population',
        compute='_compute_is_underclass_population')

    contact_origin_id = fields.Many2one(
        comodel_name='res.contact.origin', string='Contact Origin')

    is_deceased = fields.Boolean(string='Is Deceased')

    age = fields.Integer(
        string="Age", compute='_compute_age')

    type_A_capital_qty = fields.Integer(
        'Number of type A Subscription', store=True,
        compute='_compute_subscription', multi='_compute_subscription')

    type_B_capital_qty = fields.Integer(
        'Number of type B Subscription', store=True,
        compute='_compute_subscription', multi='_compute_subscription')

    type_C_capital_qty = fields.Integer(
        'Number of type C Subscription', store=True,
        compute='_compute_subscription', multi='_compute_subscription')

    is_type_A_capital_subscriptor = fields.Boolean(
        'Has a type A capital subscription', store=True,
        compute='_compute_subscription', multi='_compute_subscription')

    is_type_B_capital_subscriptor = fields.Boolean(
        'Has a type B capital subscription', store=True,
        compute='_compute_subscription', multi='_compute_subscription')

    is_type_C_capital_subscriptor = fields.Boolean(
        'Has a type C capital subscription', store=True,
        compute='_compute_subscription', multi='_compute_subscription')

    is_associated_people = fields.Boolean(
        string='Is Associated People', store=True,
        compute='_compute_is_associated_people')

    welcome_email = fields.Boolean(
        string='Welcome email sent', default=False)

    # Important : Overloaded Field Section
    customer = fields.Boolean(
        compute='_compute_customer', store=True, readonly=True)

    # Note we use selection instead of selection_add, to have a correct
    # order in the status widget
    cooperative_state = fields.Selection(
        selection=EXTRA_COOPERATIVE_STATE_SELECTION, default='not_concerned')

    # Compute Section
    @api.multi
    @api.depends('birthdate')
    def _compute_age(self):
        for partner in self:
            if partner.birthdate:
                d1 = datetime.strptime(partner.birthdate, "%Y-%m-%d").date()
                d2 = date.today()
                partner.age = relativedelta(d2, d1).years

    @api.multi
    @api.depends(
        'tmpl_reg_line_ids.date_begin', 'tmpl_reg_line_ids.date_end')
    def _compute_is_unsubscribed(self):
        for partner in self:
            # Optimization. As this function will be call by cron
            # every night, we do not realize a write, that would raise
            # useless triger for state
            if (partner.is_unsubscribed !=
                    (partner.active_tmpl_reg_line_count == 0)):
                partner.is_unsubscribed =\
                    partner.active_tmpl_reg_line_count == 0

    @api.multi
    @api.depends('fundraising_partner_type_ids')
    def _compute_is_underclass_population(self):
        xml_id = self.env.ref('louve_membership.underclass_population_type').id
        for partner in self:
            partner.is_underclass_population =\
                xml_id in partner.fundraising_partner_type_ids.ids

    @api.multi
    @api.depends(
        'invoice_ids.fundraising_category_id.is_part_A',
        'invoice_ids.fundraising_category_id.is_part_B',
        'invoice_ids.fundraising_category_id.is_part_C',
        'invoice_ids.fundraising_category_id', 'invoice_ids.state')
    def _compute_subscription(self):
        category_obj = self.env['capital.fundraising.category']
        type_A_categories = category_obj.search([('is_part_A', '=', True)])
        type_B_categories = category_obj.search([('is_part_B', '=', True)])
        type_C_categories = category_obj.search([('is_part_C', '=', True)])
        for partner in self:
            invoice_obj = self.env['account.invoice']
            # Compute Type A
            type_A_capital_qty = 0
            type_A_invoices = invoice_obj.search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['open', 'paid']),
                ('fundraising_category_id', 'in', type_A_categories.ids)])
            for invoice in type_A_invoices:
                if invoice.type == 'out_invoice':
                    type_A_capital_qty += sum(
                        invoice.mapped('invoice_line_ids.quantity'))
                else:
                    type_A_capital_qty -= sum(
                        invoice.mapped('invoice_line_ids.quantity'))

            # Compute Type B
            type_B_capital_qty = 0
            type_B_invoices = invoice_obj.search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['open', 'paid']),
                ('fundraising_category_id', 'in', type_B_categories.ids)])
            for invoice in type_B_invoices:
                if invoice.type == 'out_invoice':
                    type_B_capital_qty += sum(
                        invoice.mapped('invoice_line_ids.quantity'))
                else:
                    type_B_capital_qty -= sum(
                        invoice.mapped('invoice_line_ids.quantity'))

            # Compute Type C
            type_C_capital_qty = 0
            type_C_invoices = invoice_obj.search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['open', 'paid']),
                ('fundraising_category_id', 'in', type_C_categories.ids)])
            for invoice in type_C_invoices:
                if invoice.type == 'out_invoice':
                    type_C_capital_qty += sum(
                        invoice.mapped('invoice_line_ids.quantity'))
                else:
                    type_C_capital_qty -= sum(
                        invoice.mapped('invoice_line_ids.quantity'))

            partner.type_A_capital_qty = type_A_capital_qty
            partner.type_B_capital_qty = type_B_capital_qty
            partner.type_C_capital_qty = type_C_capital_qty
            partner.is_type_A_capital_subscriptor = type_A_capital_qty != 0
            partner.is_type_B_capital_subscriptor = type_B_capital_qty != 0
            partner.is_type_C_capital_subscriptor = type_C_capital_qty != 0

    @api.multi
    @api.depends('parent_id.is_louve_member')
    def _compute_is_associated_people(self):
        for partner in self:
            partner.is_associated_people =\
                partner.parent_id and partner.parent_id.is_louve_member

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
        if vals.get('is_louve_member', False):
            # Affect a useless default member type
            xml_id = self.env.ref('louve_membership.default_member_type').id
            vals.get('fundraising_partner_type_ids', []).append((4, xml_id))

        partner = super(ResPartner, self).create(vals)
        self._generate_associated_barcode(partner)
        return partner

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for partner in self:
            self._generate_associated_barcode(partner)
        return res

    # Custom Section
    @api.model
    def _generate_associated_barcode(self, partner):
        barcode_rule_obj = self.env['barcode.rule']
        if partner.is_associated_people and not partner.barcode_rule_id\
                and not partner.barcode:
            # Generate Associated Barcode
            barcode_rule_id = barcode_rule_obj.search(
                [('for_associated_people', '=', True)], limit=1)
            if barcode_rule_id:
                partner.barcode_rule_id = barcode_rule_id.id
            partner.generate_base()
            partner.generate_barcode()

    @api.multi
    def send_welcome_email(self):
        mail_template = self.env.ref('louve_membership.welcome_email')
        if not mail_template:
            return False
        attachment = self.env['ir.attachment'].search([
            ('name', '=',
                'La Louve - Procédure initialisation Espace Membres.pdf')])[0]

        for partner in self:
            mail_id = mail_template.send_mail(partner.id)
            mail = self.env['mail.mail'].browse(mail_id)
            if attachment:
                mail.attachment_ids = [(6, 0, [attachment.id])]
            partner.welcome_email = True
        return True

    # CRON section
    @api.model
    def update_is_unsubscribed(self):
        partners = self.search([])
        partners._compute_is_unsubscribed()

    @api.model
    def send_welcome_emails(self):
        partners = self.search([
            ('welcome_email', '=', False),
            ('is_type_A_capital_subscriptor', '=', True),
            ('is_unsubscribed', '=', False),
        ])
        partners.send_welcome_email()

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

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name.isdigit():
            partners = self.search([
                ('barcode_base', '=', name),
                ('is_louve_member', '=', True)], limit=limit)
            if partners:
                return partners.name_get()
        return super(ResPartner, self).name_search(
            name=name, args=args, operator=operator, limit=limit)

    @api.multi
    def name_get(self):
        res = []
        i = 0
        original_res = super(ResPartner, self).name_get()
        for partner in self:
            if partner.is_louve_member:
                res.append((
                    partner.id,
                    '%s - %s' % (partner.barcode_base, original_res[i][1])))
            else:
                res.append((partner.id, original_res[i][1]))
            i += 1
        return res
