# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Some code from https://www.odoo.com/apps/modules/8.0/birth_date_age/
# Copyright (C) Sythil

import base64

import pytz
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.addons.queue_job.job import job
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval

NUMBER_OF_PARTNERS_PER_JOB = 100

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

    # New Column Section

    # Add field in res partner
    payment_method_count = fields.Integer()
    opt_out = fields.Boolean(default=False)

    is_member = fields.Boolean(
        'Is Member',
        compute="_compute_is_member",
        compute_sudo=True,
        store=True,
        readonly=True,
    )
    is_former_member = fields.Boolean(
        "Is Former Member",
        compute="_compute_is_former_member",
        compute_sudo=True,
        store=True,
        readonly=True,
    )
    is_former_associated_people = fields.Boolean(
        "Is Former Associated People",
        compute="_compute_is_former_associated_people",
        compute_sudo=True,
        store=True,
        readonly=True,
    )
    is_interested_people = fields.Boolean(
        "Is Interested People",
        compute="_compute_is_interested_people",
        compute_sudo=True,
        readonly=True,
        store=True,
    )
    is_worker_member = fields.Boolean(
        "Is Worker Member",
        compute="_compute_is_worker_member",
        compute_sudo=True,
        readonly=True,
        store=True,
    )
    is_unpayed = fields.Boolean(
        string='Unpayed',
        help="Check this box, if the partner has late"
             " payments for him capital subscriptions. this will prevent him"
             " to buy.",
    )
    is_unsubscribed = fields.Boolean(
        string='Unsubscribed',
        help="Computed field."
             " This box is checked if the user is not linked"
             " to a template registration.",
        compute="_compute_is_unsubscribed",
        compute_sudo=True,
        store=True,
    )
    unsubscription_date = fields.Date(
        string='Unsubscription Date',
        compute='_compute_is_unsubscribed',
        compute_sudo=True,
        store=True,
    )
    is_underclass_population = fields.Boolean(
        'is Underclass Population',
        compute='_compute_is_underclass_population',
    )
    is_associated_people = fields.Boolean(
        string='Is Associated People',
        compute='_compute_is_associated_people',
        compute_sudo=True,
        store=True,
    )
    is_designated_buyer = fields.Boolean(
        string='Designated buyer'
    )
    temp_coop_number = fields.Char('Temporary number')
    contact_origin_id = fields.One2many(
        'event.registration',
        'partner_id',
        string='Contact Origin',
    )
    is_deceased = fields.Boolean(string='Is Deceased')
    date_of_death = fields.Date(string="Date of Death")
    age = fields.Integer("Age", compute='_compute_age')

    partner_owned_share_ids = fields.One2many(
        'res.partner.owned.share',
        'partner_id',
        string="Partner Owned Shares")

    total_partner_owned_share = fields.Integer(
        string="Total Owned Shares",
        compute="_compute_total_partner_owned_share",
        store=True,
    )

    deactivated_date = fields.Date()

    welcome_email = fields.Boolean(
        string='Welcome email sent', default=False)

    # Important : Overloaded Field Section
    customer = fields.Boolean(
        compute='_compute_customer',
        store=True,
        readonly=True,
    )

    # Note we use selection instead of selection_add, to have a correct
    # order in the status widget
    cooperative_state = fields.Selection(
        selection=EXTRA_COOPERATIVE_STATE_SELECTION, default='not_concerned')

    working_state = fields.Selection(
        selection=EXTRA_COOPERATIVE_STATE_SELECTION)

    nb_associated_people = fields.Integer(
        'Number of Associated People',
        compute="_compute_number_of_associated_people",
        store=True)

    parent_member_num = fields.Integer(
        string="Parent Number",
        related='parent_id.barcode_base',
        store=True,
    )
    badge_distribution_date = fields.Date("Badge Distribution")
    badge_to_distribute = fields.Boolean(
        "Badge to distribute",
        store=True,
        compute="_compute_badge_to_distribute",
    )
    badge_print_date = fields.Date("Badge Print Date")
    contact_us_message = fields.Html(
        string="Contact Us Message",
        translate=True,
    )
    force_customer = fields.Boolean(
        "Force Customer",
        default=False,
    )
    inform_ids = fields.Many2many(
        'res.partner.inform',
        string='Informé que',
    )
    shift_type = fields.Selection(
        string='Shift type',
        compute='_compute_shift_type',
        store=True,
    )
    current_template_name = fields.Char(
        string='Current Template',
        compute='_compute_current_template',
        store=True
    )
    current_template_week_name = fields.Char(
        string='Current Template Week',
        compute='_compute_current_template',
        store=True
    ) 
    is_minor_child = fields.Boolean(string='Enfant mineur')
    leader_ids = fields.Many2many(
        string='Shift Leaders',
        comodel_name='res.partner',
        relation='partner_leader_rel',
        column1='leader_id',
        column2='partner_id',
        compute='_compute_current_template',
    )

    event_event_id = fields.Many2one('event.event')
    display_name = fields.Char(
        compute='_compute_display_name', store=True, index=True)

    @api.depends('is_company', 'name', 'parent_id.name', 'type',
        'company_name', 'barcode_base')
    def _compute_display_name(self):
        '''
        Override this function to add dependency to barcode_base 
        '''
        super(ResPartner, self)._compute_display_name()

    @api.onchange('birthdate_date')
    def _onchange_birthdate_date(self):
        self._check_partner_birthdate_date()

    # Constraint Section
    @api.constrains('birthdate_date')
    def _check_partner_birthdate_date(self):
        """ Check minor child's birth date """
        for partner in self:
            if partner.is_minor_child and partner.birthdate_date:
                if partner.age < 18:
                    raise ValidationError(_(
                        "Cette personne a plus de 18 ans et ne peux pas être "
                        "saisie comme un enfant mineur.")
                    )

    @api.constrains(
        'is_member', 'parent_id',
        'is_associated_people', 'total_partner_owned_share',
    )
    def _check_partner_type(self):
        '''
        @Function to add a constraint on partner type
            - If a partner has shares, he cannot be an associated member
        '''
        for partner in self:
            if (
                partner.parent_id
                and partner.parent_id.is_member
                and partner.total_partner_owned_share > 0
            ):
                raise ValidationError(_(
                    "You can't be an associated people if you have shares ! "
                    "Empty the parent_id field to be allowed to write others "
                    "changes"))

    @api.multi
    @api.constrains('nb_associated_people')
    def _check_number_of_associated_people(self):
        '''
        @Function to add a constraint on member
            - A member cannot have number_of_associated_people higher than max.
        '''
        config_param_env = self.env['ir.config_parameter']
        key_max_nb = 'coop_membership.max_nb_associated_people'
        max_nb = safe_eval(config_param_env.sudo().get_param(key_max_nb, '0'))
        key_avail_check = 'coop_membership.associated_people_available'
        avail_check = config_param_env.sudo().get_param(
            key_avail_check, 'unlimited')
        for rec in self:
            if avail_check == 'limited' and rec.is_member and \
                    rec.nb_associated_people > max_nb:
                raise ValidationError(_(
                    "The maximum number of associated people has "
                    "been exceeded."))

    @api.multi
    @api.depends('is_associated_people', 'parent_id.shift_type')
    def _compute_shift_type(self):
        for partner in self.sorted(key=lambda p: p.is_associated_people):
            if partner.is_associated_people and partner.parent_id:
                partner.shift_type = partner.parent_id.shift_type
            else:
                partner.shift_type = 'standard'

    @api.multi
    @api.depends('badge_distribution_date', 'badge_print_date')
    def _compute_badge_to_distribute(self):
        for record in self:
            badge_to_distribute = False
            if record.badge_print_date:
                if not record.badge_distribution_date or \
                        record.badge_distribution_date < \
                        record.badge_print_date:
                    badge_to_distribute = True
            record.badge_to_distribute = badge_to_distribute

    @api.multi
    def force_customer_button(self):
        for record in self:
            record.force_customer = True
        return True

    @api.multi
    def force_supplier_button(self):
        for record in self:
            record.force_customer = False
        return True

    @api.multi
    def update_badge_print_date(self):
        for record in self:
            record.badge_print_date = fields.Date.context_today(self)

    # Compute Section
    @api.multi
    @api.depends('birthdate_date')
    def _compute_age(self):
        for partner in self:
            if partner.birthdate_date:
                d1 = partner.birthdate_date
                d2 = fields.Date.today()
                partner.age = relativedelta(d2, d1).years

    @api.multi
    def set_messages_contact(self):
        self.ensure_one()
        message = self.env.user.company_id.contact_us_message
        self.write({
            'contact_us_message': message
        })
        return True

    @api.multi
    @api.depends(
        'tmpl_reg_line_ids.date_begin', 'tmpl_reg_line_ids.date_end')
    def _compute_is_unsubscribed(self):
        for partner in self:
            # Optimization. As this function will be call by cron
            # every night, we do not realize a write, that would raise
            # useless triger for state
            today = fields.Date.context_today(self)
            leave_none_defined = partner.leave_ids.filtered(
                lambda l: (l.start_date or today) <= today <= (l.stop_date or today)
                and l.non_defined_leave and l.state == 'done')
            no_reg_line = partner.active_tmpl_reg_line_count == 0
            is_unsubscribed = (no_reg_line and not leave_none_defined)
            if partner.is_unsubscribed != is_unsubscribed:
                partner.is_unsubscribed = is_unsubscribed

            if partner.active_tmpl_reg_line_count:
                partner.unsubscription_date = False

            # Auto remove partner from squadleader of team
            if partner.is_unsubscribed:
                templates = self.env['shift.template'].search([
                    ('user_ids', 'in', partner.id),
                ])
                # TODO Check here to re add this partner as a leader
                for template in templates:
                    if len(template.user_ids) >= 2:
                        template.write({
                            'user_ids': [(3, partner.id)],
                            'removed_user_ids': [(4, partner.id)],
                        })

                tmpl_reg_lines = partner.tmpl_reg_line_ids.filtered(
                    lambda tmpl_rgl: tmpl_rgl.date_end).sorted(
                    lambda tmpl_rgl: tmpl_rgl.id
                )

                if tmpl_reg_lines:
                    partner.unsubscription_date = fields.Date.from_string(
                        tmpl_reg_lines[-1].date_end
                    )

    @api.multi
    @api.depends('fundraising_partner_type_ids')
    def _compute_is_underclass_population(self):
        xml_id = self.env.ref('coop_membership.underclass_population_type').id
        for partner in self:
            partner.is_underclass_population = \
                xml_id in partner.fundraising_partner_type_ids.ids

    @api.multi
    @api.depends('partner_owned_share_ids',
                 'partner_owned_share_ids.owned_share')
    def _compute_total_partner_owned_share(self):
        for partner in self:
            partner.total_partner_owned_share = \
                sum(partner_ownedshare.owned_share
                    for partner_ownedshare in partner.partner_owned_share_ids)
            # Update when number of shares reaches "0"
            partner._update_when_number_of_shares_reaches_0()

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
                    self.env['account.invoice'].sudo().search_count(
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
            partner.is_associated_people = \
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
            worker_shares = partner_owned_share_env.sudo().search_count(
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

    @api.depends('cooperative_state', 'force_customer')
    def _compute_customer(self):
        for partner in self:
            partner.customer = (
                partner.cooperative_state in self.COOPERATIVE_STATE_CUSTOMER
                or partner.force_customer
            )

    @api.depends('child_ids')
    def _compute_number_of_associated_people(self):
        for partner in self:
            if (
                (partner.is_member or partner.is_former_member)
                and partner.child_ids
            ):
                partner.nb_associated_people = sum([
                    (
                        p.is_associated_people
                        or p.is_former_associated_people
                    ) and 1 or 0
                    for p in partner.child_ids
                ])
            else:
                partner.nb_associated_people = 0

    @api.multi
    @api.depends('tmpl_reg_ids', 'tmpl_reg_ids.is_current')
    def _compute_current_template(self):
        for partner in self:
            current_template = False
            reg = partner.tmpl_reg_ids.filtered(
                lambda r: r.is_current)
            if reg:
                current_template = reg[0].shift_template_id
            else:
                reg = partner.tmpl_reg_ids.filtered(
                    lambda r: r.is_future)
                if reg:
                    current_template = reg[0].shift_template_id
            if current_template:
                partner.leader_ids = current_template.user_ids
                partner.current_template_name = current_template.name
                partner.current_template_week_name = current_template.week_name
            else:
                partner.leader_ids = False
                partner.current_template_name = False
                partner.current_template_week_name = False

    # Overload Section
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('allow_to_search_barcode_base', False):
            barcode_base_clauses = filter(
                lambda clause: clause[0] == 'barcode_base'
                and not clause[-1].isdigit(),
                args
            )
            for barcode_base_clause in barcode_base_clauses:
                barcode_base_clause[0] = u'display_name'
                barcode_base_clause[1] = u'ilike'
        return super(ResPartner, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('allow_to_search_barcode_base', False):
            barcode_base_clauses = filter(
                lambda clause: clause[0] == 'barcode_base'
                and not clause[-1].isdigit(),
                domain
            )
            for barcode_base_clause in barcode_base_clauses:
                barcode_base_clause[0] = u'display_name'
                barcode_base_clause[1] = u'ilike'
        return super(ResPartner, self).read_group(domain, fields, groupby,
            offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)
        self._generate_associated_barcode(partner)
        self.check_designated_buyer(partner)
        return partner

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for partner in self:
            self._generate_associated_barcode(partner)
        # Recompute display_name if needed
        if (
            'name' not in vals
            and (
                'barcode_base' in vals
                or 'is_member' in vals
            )
        ):
            for partner in self:
                partner.name = partner.name
        if 'parent_id' in vals:
            # Update is_former_associated_people to true
            # if an associated member had been removed from its parent
            if not vals.get('parent_id'):
                asscociated_member_ids = self.filtered('is_associated_people')
                for partner in self:
                    if partner in asscociated_member_ids:
                        partner.is_former_associated_people = True
        return res

    # Custom Section
    @api.model
    def check_designated_buyer(self, partner):
        company_id = self.env.user.company_id
        maximum_active_days = company_id.maximum_active_days
        today = fields.Date.from_string(fields.Date.today())
        if partner.is_designated_buyer:
            partner.deactivated_date = \
                today + relativedelta(days=maximum_active_days)

    @api.model
    def _generate_associated_barcode(self, partner):
        barcode_rule_obj = self.env['barcode.rule']
        if partner.is_associated_people and not partner.barcode_rule_id \
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
    def update_is_unsubscribed_manually(self, partner_ids):
        """
        This is util function which call by Cron with passing partner_ids
        as arguments.
        It helps to test _compute_is_unsubscribed function easily
        """
        partners = self.browse(partner_ids)
        partners._compute_is_unsubscribed()

    @api.model
    def update_is_unsubscribed(self):
        partners = self.search([])
        partners._compute_is_unsubscribed()

    @api.model
    def send_welcome_emails(self, limit=None):
        partners = self.search([
            ('welcome_email', '=', False),
            ('is_worker_member', '=', True),
            ('is_unsubscribed', '=', False),
        ], limit=limit)
        partners.send_welcome_email()

    @api.model
    def update_welcome_email_manually(self, limit=None):
        partners = self.search([
            ('welcome_email', '=', False),
            ('is_worker_member', '=', True),
            ('is_unsubscribed', '=', False),
        ], limit=limit)
        partners.write({
            'welcome_email': True
        })

    @api.model
    def deactivate_designated_buyer(self):
        partners = self.search([
            ('deactivated_date', '=', fields.Date.today())
        ])
        partners.write({
            'active': False
        })

    @api.model
    def cron_send_notify_mirror_children_email(self):
        today_dt = fields.Date.from_string(fields.Date.today())
        today_dt_last_18years = today_dt - relativedelta(years=18) + \
            relativedelta(weeks=2)
        today_dt_last_18years_tr = today_dt_last_18years.strftime("%Y-%m-%d")
        query = """
            SELECT id
            FROM res_partner
            WHERE to_date(cast(birthdate_date as TEXT),'YYYY-MM-DD') <= %s
            AND parent_id IS NOT NULL
            AND is_associated_people IS TRUE
            AND is_minor_child IS TRUE
        """
        self.env.cr.execute(
            query, (today_dt_last_18years_tr,)
        )
        result = self.env.cr.fetchall()
        if result:
            notify_email_template = self.env.ref(
                'coop_membership.notify_mirror_children_email')
            to_notify_member_ids = [item[0] for item in result]
            to_notify_members = self.browse(to_notify_member_ids)
            if notify_email_template:
                for member in to_notify_members:
                    notify_email_template.send_mail(member.id)

    @api.model
    def cron_update_mirror_children(self):
        today_dt = fields.Date.from_string(fields.Date.today())
        today_dt_last_18years = today_dt - relativedelta(years=18)
        today_dt_last_18years_tr = today_dt_last_18years.strftime("%Y-%m-%d")
        query = """
            SELECT id
            FROM res_partner
            WHERE to_date(cast(birthdate_date as TEXT),'YYYY-MM-DD') <= %s
            AND parent_id IS NOT NULL
            AND is_associated_people IS TRUE
            AND is_minor_child IS TRUE
            """
        self.env.cr.execute(
            query, (today_dt_last_18years_tr,)
        )
        result = self.env.cr.fetchall()
        if result:
            to_update_member_ids = [item[0] for item in result]
            to_update_members = self.browse(to_update_member_ids)
            to_update_members.write({
                'parent_id': False,
            })

            # Need to write again field `is_former_associated_people`
            to_update_members.write({
                'is_former_associated_people': False,
                'is_member': True,
            })

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
        is_member_unsubscribed = self._context.get(
            'member_unsubscribed', False)
        if name.isdigit():
            domain = [('barcode_base', '=', name),
                      ('is_member', '=', True)]

            if is_member_unsubscribed:
                domain.append(('is_unsubscribed', '=', False))

            partners = self.search(domain, limit=limit)
            if partners:
                return partners.name_get()
        return super(ResPartner, self).name_search(
            name=name, args=args, operator=operator, limit=limit)

    @api.multi
    def name_get(self):
        res = []
        i = 0
        original_res = super(ResPartner, self).name_get()
        only_show_barcode_base = self._context.get(
            'only_show_barcode_base', False)

        for partner in self:
            original_value = original_res[i][1]
            # S#24956:
            # 2) In the list of membres in the potentially present for the
            # shift, in the “Contact” column, some members have their numbers
            # next to their name, others do not. We want all members to have
            # their numbers next to their names. See attached screenshot.
            name_get_values = (partner.id, original_value)
            if partner.barcode_base:
                name_get_values = (
                    partner.id,
                    '%s - %s' % (partner.barcode_base, original_value)
                )
            if only_show_barcode_base:
                name_get_values = (partner.id, str(partner.barcode_base))

            res.append(name_get_values)
            i += 1
        return res

    @api.multi
    def get_next_shift_date(self, start_date=None):
        '''
        @Function to get Next Shift Date of a member
        '''
        self.ensure_one()
        shift_reg = self.get_next_shift(start_date)
        if not shift_reg:
            return False, False

        next_shift_time = shift_reg.date_begin
        next_shift_date = False

        # Convert Next Shift Time into Local Time
        if next_shift_time:
            tz_name = self._context.get('tz', self.env.user.tz) or 'utc'
            utc_timestamp = pytz.utc.localize(
                next_shift_time, is_dst=False)
            context_tz = pytz.timezone(tz_name)
            start_date_object_tz = utc_timestamp.astimezone(context_tz)
            next_shift_date = start_date_object_tz.strftime('%Y-%m-%d')

        return next_shift_time, next_shift_date

    @api.multi
    def get_next_shift(self, start_date=None):
        shift_registration_env = self.env['shift.registration']
        for partner in self:
            start_date = start_date or fields.Datetime.now()

            # Search for next shifts
            shift_regs = shift_registration_env.search([
                ('partner_id', '=', partner.id),
                ('template_created', '=', True),
                ('date_begin', '>=', start_date)
            ])

            if shift_regs:
                # Sorting found shift
                shift_regs = shift_regs.sorted(
                    key=lambda shift: shift.date_begin)
                return shift_regs[0]

        return False

    @api.multi
    def _mass_change_team(self):
        active_ids = self._context.get('active_ids', [])
        partner_ids = active_ids
        if partner_ids:
            partner_id = partner_ids[0]
            partner_ids.remove(partner_ids[0])
            changed_team_ids = []
            return {
                'name': _('Change Team'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_partner_id': partner_id,
                            'partner_ids': partner_ids,
                            'changed_team_ids': changed_team_ids,
                            },
            }

    @api.multi
    def _update_when_number_of_shares_reaches_0(self):
        self.ensure_one()
        # only take into count member that already
        # has partner_owned_share before
        invoice_states = []
        for partner_share in self.partner_owned_share_ids:
            invoice_states += [
                invoice.state in ['open', 'paid', 'cancel'] for
                invoice in partner_share.related_invoice_ids
            ]
        # all invoice states != 'draft'
        invoice_states = all(invoice_states)
        if (
            self.partner_owned_share_ids
            and self.partner_owned_share_ids[0].related_invoice_ids
            and invoice_states
            and self.total_partner_owned_share == 0
        ):
            # Set date and for shift template
            for tmpl_reg in self.tmpl_reg_line_ids:
                if (
                    not tmpl_reg.date_end
                    or tmpl_reg.date_end > fields.Date.today()
                ):
                    tmpl_reg.write({'date_end': fields.Date.today()})
            # Set date begin for shift ticket
            for reg in self.registration_ids:
                if reg.date_begin > fields.Datetime.now():
                    reg.write({'date_begin': fields.Datetime.now()})
            # Update Mailling opt out
            # issue: disappear property_account_payable/recievable_id
            # when creating a child partner
            # (open wizard to add child contact)
            # when creating a associate people from contact tab,
            # the total_partner_owned_share of new partner is zero,
            # so if we don't check partner_owned_share_ids,
            # this opt_out is set for new partner also
            # and somehow, property_account are disappeared on parent partner.
            # ==> add a check partner_owned_shared_ids to only apply
            # for partner
            # which already has partner_owned_share
            self.write({'opt_out': True})
        return True

    @api.multi
    def generate_pdf(self, report_name):
        return self.env['report'].with_context(
            active_model=self._name,
            active_ids=self.ids,
        ).get_pdf(self, report_name)

    @api.multi
    def attach_report_in_mail(self):
        self.ensure_one()
        report_name = 'coop_membership.member_contract_template'
        report = self.generate_pdf(report_name)
        encoded_report = base64.encodestring(report)
        filename = 'Member Contract'
        # create the new ir_attachment
        attachment_value = {
            'name': filename,
            'res_name': filename,
            'res_model': 'res.partner',
            'datas': encoded_report,
            'datas_fname': filename + '.pdf',
        }
        new_attachment = self.env['ir.attachment'].create(attachment_value)
        return new_attachment

    @api.multi
    def update_shift_type(self):
        partners_ids = self.ids
        chunks = [
            partners_ids[i: i + NUMBER_OF_PARTNERS_PER_JOB]
            for i in range(0, len(partners_ids), NUMBER_OF_PARTNERS_PER_JOB)
        ]
        # Create jobs
        for chunk in chunks:
            self.with_delay().update_shift_type_res_partner_session_job(chunk)
        return True

    def create_related_users(self):
        users = self.env['res.users']
        for partner in self:
            users |= partner.create_related_user()
        view = self.env.ref('base.view_users_form')
        return {
            'name': _('Users'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'res.users',
            'target': 'current',
            'view_id': view.id,
            'res_id': users and users[0].id
        }

    def create_related_user(self):
        self.ensure_one()
        partner = self
        user = ResUsers = self.env['res.users']
        if partner.email and not partner.user_ids:
            existed = ResUsers.search([
                ('login', '=', partner.email),
                '|', ('active', '=', False), ('active', '=', True)
            ], limit=1)
            if existed:
                raise UserError(_("Another user is already registered using this email address."))
            vals = {
                'login': partner.email,
                'partner_id': partner.id
            }
            user = ResUsers.create(vals)
        return user

    @api.multi
    def create_job_to_compute_current_template(self):
        partners_ids = self.ids
        chunks = [
            partners_ids[i: i + NUMBER_OF_PARTNERS_PER_JOB]
            for i in range(0, len(partners_ids), NUMBER_OF_PARTNERS_PER_JOB)
        ]
        # Create jobs
        for chunk in chunks:
            self.with_delay().update_member_current_template_name(chunk)
        return True

    @api.model
    def cron_compute_current_template(self, offset=0, partner_limit=1000):
        partner_count = self.env['res.partner'].search_count([])
        while offset < partner_count:
            description = "Update current template name from {start} to {end}".format(
                start=offset,
                end=offset+partner_limit-1
            )
            if partner_count < partner_limit:
                self.update_member_current_template_name_limit(offset, partner_limit)
            else:
                self.with_delay(description=description).update_member_current_template_name_limit(
                    offset, partner_limit)
            offset += partner_limit

    @job
    def update_member_current_template_name_limit(self, offset, limit):
        """ Job for Updating Current Shift Template Name """
        partners = self.env['res.partner'].search([], offset, limit)
        partners._compute_current_template()

    @job
    def update_shift_type_res_partner_session_job(
            self, session_list):
        """ Job for compute shift type """
        partners = self.browse(session_list)
        partners._compute_shift_type()

    @job
    def update_member_current_template_name(self, partner_ids):
        """ Job for Updating Current Shift Template Name """
        partners = self.browse(partner_ids)
        partners._compute_current_template()
