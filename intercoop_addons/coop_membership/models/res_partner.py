# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Some code from https://www.odoo.com/apps/modules/8.0/birth_date_age/
# Copyright (C) Sythil

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import pytz
from openerp.exceptions import ValidationError
from openerp import models, fields, api, _


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
        ('o', 'other'),
    ]

    # New Column Section
    is_member = fields.Boolean('Is Member',
                               compute="_compute_is_member",
                               store=True,
                               readonly=True)

    is_former_member = fields.Boolean("Is Former Member",
                                      compute="_compute_is_former_member",
                                      store=True, readonly=True)

    is_former_associated_people = fields.Boolean(
                                "Is Former Associated People",
                                compute="_compute_is_former_associated_people",
                                store=True, readonly=True)

    is_interested_people = fields.Boolean(
        "Is Interested People",
        compute="_compute_is_interested_people",
        readonly=True, store=True)

    is_worker_member = fields.Boolean(
        "Is Worker Member",
        compute="_compute_is_worker_member",
        readonly=True, store=True)

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

    temp_coop_number = fields.Char('Temporary number')

    is_underclass_population = fields.Boolean(
        'is Underclass Population',
        compute='_compute_is_underclass_population')

    contact_origin_id = fields.Many2one(
        comodel_name='res.contact.origin', string='Contact Origin')

    is_deceased = fields.Boolean(string='Is Deceased')

    date_of_death = fields.Date(string="Date of Death")

    age = fields.Integer(
        string="Age", compute='_compute_age')

    partner_owned_share_ids = fields.One2many(
        'res.partner.owned.share',
        'partner_id',
        string="Partner Owned Shares")

    total_partner_owned_share = fields.Integer(
        string="Total Owned Shares",
        compute="_compute_total_partner_owned_share",
        store=True)

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

    # Constraint Section
    @api.multi
    @api.constrains(
        'is_member',
        'parent_id',
        'parent_id.is_member',
        'total_partner_owned_share')
    def _check_partner_type(self):
        '''
        @Function to add a constraint on partner type
            - If a partner has shares, he cannot be an associated member
        '''
        for partner in self:
            partner_parent = partner.parent_id
            if partner_parent and partner_parent.is_member and \
                    partner.total_partner_owned_share > 0:
                raise ValidationError(
                    _("You can't be an " +
                      "associated people if you have shares ! " +
                      "Empty the parent_id field to be allowed " +
                      "to write others changes"))

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
        xml_id = self.env.ref('coop_membership.underclass_population_type').id
        for partner in self:
            partner.is_underclass_population =\
                xml_id in partner.fundraising_partner_type_ids.ids

    @api.multi
    @api.depends('partner_owned_share_ids',
                 'partner_owned_share_ids.owned_share')
    def _compute_total_partner_owned_share(self):
        for partner in self:
            partner.total_partner_owned_share = \
                sum(partner_ownedshare.owned_share
                    for partner_ownedshare in partner.partner_owned_share_ids)

    @api.multi
    @api.depends('total_partner_owned_share')
    def _compute_is_member(self):
        '''
        @Function to identify if a partner is a member:
            - A partner is a member if he/she has shares of any type
        '''
        for partner in self:
            partner.is_member = partner.total_partner_owned_share > 0

    @api.multi
    @api.depends("total_partner_owned_share")
    def _compute_is_former_member(self):
        '''
        @Function to compute the value of is former member
        '''
        for partner in self:
            if partner.total_partner_owned_share == 0:
                fundraising_count = \
                    self.env['account.invoice'].search_count(
                        [('partner_id', '=', partner.id),
                         ('fundraising_category_id', '!=', False),
                         ('state', 'in', ('open', 'paid'))])
                if fundraising_count:
                    partner.is_former_member = True
                else:
                    partner.is_former_member = False
            else:
                partner.is_former_member = False

    @api.multi
    @api.depends('is_member', 'is_associated_people',
                 'is_former_member', 'is_former_associated_people', 'supplier')
    def _compute_is_interested_people(self):
        '''
        @Function to compute data for the field is_interested_people
            - True if: a partner is not a member AND is not associated people
            AND is not a supplier
        '''
        for partner in self:
            partner.is_interested_people = \
                (not partner.is_member) and \
                (not partner.is_associated_people) and \
                (not partner.is_former_associated_people) and \
                (not partner.is_former_member) and \
                (not partner.supplier) or False

    @api.multi
    @api.depends('is_member', 'parent_id.is_member')
    def _compute_is_associated_people(self):
        for partner in self:
            partner.is_associated_people =\
                partner.parent_id and \
                partner.parent_id.is_member and (not partner.is_member)

    @api.multi
    @api.depends('parent_id', 'parent_id.is_former_member')
    def _compute_is_former_associated_people(self):
        for partner in self:
            partner.is_former_associated_people = \
                partner.parent_id and partner.parent_id.is_former_member

    @api.multi
    @api.depends(
        'partner_owned_share_ids',
        'partner_owned_share_ids.category_id',
        'partner_owned_share_ids.category_id.is_worker_capital_category',
        'partner_owned_share_ids.owned_share')
    def _compute_is_worker_member(self):
        '''
        @Function to compute data for the field is_worker_member:
            - True if a member has shares in Worker Capital Category
        '''
        partner_owned_share_env = self.env['res.partner.owned.share']
        for partner in self:
            worker_shares = partner_owned_share_env.search_count(
                [('partner_id', '=', partner.id),
                 ('category_id.is_worker_capital_category', '=', True),
                 ('owned_share', '>', 0)])
            partner.is_worker_member = worker_shares and True or False

    @api.depends(
        'working_state', 'is_unpayed', 'is_unsubscribed',
        'is_worker_member', 'is_associated_people',
        'parent_id.cooperative_state')
    @api.multi
    def _compute_cooperative_state(self):
        for partner in self:
            if partner.is_associated_people:
                # Associated People
                partner.cooperative_state = partner.parent_id.cooperative_state
            elif partner.is_worker_member:
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
        partner = super(ResPartner, self).create(vals)
        self._generate_associated_barcode(partner)
        return partner

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for partner in self:
            self._generate_associated_barcode(partner)
        # Recompute display_name if needed
        if ('barcode_base' in vals or 'is_member' in vals) and (
                not 'name' in vals):
            for partner in self:
                partner.name = partner.name
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
        mail_template = self.env.ref('coop_membership.welcome_email')
        if not mail_template:
            return False

        for partner in self:
            mail_template.send_mail(partner.id)
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
            ('is_worker_member', '=', True),
            ('is_unsubscribed', '=', False),
        ])
        partners.send_welcome_email()

    # View section
    @api.multi
    def set_underclass_population(self):
        xml_id = self.env.ref('coop_membership.underclass_population_type').id
        for partner in self:
            partner.fundraising_partner_type_ids = [(4, xml_id)]

    @api.multi
    def remove_underclass_population(self):
        xml_id = self.env.ref('coop_membership.underclass_population_type').id
        for partner in self:
            partner.fundraising_partner_type_ids = [(3, xml_id)]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name.isdigit():
            partners = self.search([
                ('barcode_base', '=', name),
                ('is_member', '=', True)], limit=limit)
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
            if partner.is_member:
                res.append((
                    partner.id,
                    '%s - %s' % (partner.barcode_base, original_res[i][1])))
            else:
                res.append((partner.id, original_res[i][1]))
            i += 1
        return res

    @api.multi
    def get_next_shift_date(self):
        '''
        @Function to get Next Shift Date of a member
        '''
        self.ensure_one()
        shift_registration_env = self.env['shift.registration']

        # Search for next shifts
        shift_regs = shift_registration_env.search([
            ('partner_id', '=', self.id),
            ('template_created', '=', True),
            ('date_begin', '>=', fields.Datetime.now())
        ])

        next_shift_time = False
        next_shift_date = False
        if shift_regs:
            # Sorting found shift
            shift_regs.sorted(key=lambda shift: shift.date_begin)
            next_shift_time = shift_regs[0].date_begin

        # Convert Next Shift Time into Local Time
        if next_shift_time:
            next_shift_time_obj = datetime.strptime(
                next_shift_time, '%Y-%m-%d %H:%M:%S')
            tz_name = self._context.get('tz') or self.env.user.tz
            utc_timestamp = pytz.utc.localize(
                next_shift_time_obj, is_dst=False)
            context_tz = pytz.timezone(tz_name)
            start_date_object_tz = utc_timestamp.astimezone(context_tz)
            next_shift_date = start_date_object_tz.strftime('%Y-%m-%d')

        return next_shift_time, next_shift_date
