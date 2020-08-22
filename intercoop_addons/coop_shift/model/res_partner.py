# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

from .date_tools import conflict_period


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Constants Section
    SHIFT_TYPE_SELECTION = [
        ('standard', 'Standard'),
        ('ftop', 'FTOP'),
    ]

    WORKING_STATE_SELECTION = [
        ('exempted', 'Exempted'),
        ('vacation', 'On Vacation'),
        ('up_to_date', 'Up to date'),
        ('alert', 'Alert'),
        ('suspended', 'Suspended'),
        ('delay', 'Delay'),
        ('blocked', 'Blocked'),
    ]

    # Columns Section
    leave_ids = fields.One2many(
        comodel_name='shift.leave', inverse_name='partner_id', string='Leaves')

    leave_qty = fields.Integer(
        string='Number of Shift Leaves', compute='_compute_leave_qty')
    current_leave_info = fields.Char(
        string='Current Leave Information', compute='_compute_leave_qty')

    registration_ids = fields.One2many(
        'shift.registration', "partner_id", 'Registrations')

    upcoming_registration_count = fields.Integer(
        "Number of registrations", compute="_compute_registration_counts")
    next_registration_id = fields.One2many(
        'shift.registration', "partner_id", 'Next Registration',
        compute="_compute_registration_counts")

    next_abcd_registrations = fields.One2many(
        'shift.registration', "partner_id", 'Prochains Services',
        compute="_compute_registration_counts")

    next_ftop_registration_date = fields.Datetime(
        string='Prochain Décompte Volant',
        compute="_compute_registration_counts")

    tmpl_reg_ids = fields.One2many(
        'shift.template.registration', "partner_id",
        'Template Registrations')

    tmpl_reg_line_ids = fields.One2many(
        'shift.template.registration.line', "partner_id",
        'Template Registration Lines')

    tmpl_registration_count = fields.Integer(
        "Number of Template registrations",
        compute="_compute_registration_counts")

    active_tmpl_reg_line_count = fields.Integer(
        "Number of active registration lines",
        compute="_compute_registration_counts")

    current_tmpl_reg_line = fields.Char(
        string="Current Template Registration Lines",
        compute="_compute_registration_counts"
    )

    current_template_name = fields.Char(
        string='Current Template', compute='_compute_current_template_name')

    is_squadleader = fields.Boolean(
        "is an active Squadleader", compute="_compute_is_squadleader")
    template_ids = fields.Many2many(
        'shift.template', 'res_partner_shift_template_rel',
        'partner_id', 'shift_template_id', string='Leader on these templates')

    is_exempted = fields.Boolean(
        "Is Exempted", compute='_compute_is_exempted')

    is_vacation = fields.Boolean(
        "Is on Vacation", compute='_compute_is_vacation')

    is_blocked = fields.Boolean(
        string='Blocked', help="Check this box to manually block this user.")

    shift_type = fields.Selection(
        readonly=1, required=1,
        selection=SHIFT_TYPE_SELECTION, string='Shift type',
        default='standard')

    working_state = fields.Selection(
        selection=WORKING_STATE_SELECTION, string='Working State', store=True,
        compute='_compute_working_state', help="This state depends on the"
        " shifts realized by the partner.")

    cooperative_state = fields.Selection(
        selection=WORKING_STATE_SELECTION, string='Cooperative State',
        store=True, compute='_compute_cooperative_state', help="This state"
        " depends on the 'Working State' and extra custom settings.")

    # Fields for final standard and ftop points
    final_standard_point = fields.Float(
        string='Final Standard points', compute='compute_final_standard_point',
        store=True)

    final_ftop_point = fields.Float(
        string='Final FTOP points', compute='compute_final_ftop_point',
        store=True)

    display_std_points = fields.Float(
        string="Actual Current Standard Points",
        compute="compute_display_counter_point",
        store=True
    )

    display_ftop_points = fields.Float(
        string="Actual Current FTOP Points",
        compute="compute_display_counter_point",
        store=True
    )

    date_alert_stop = fields.Date(
        string='End Alert Date', compute='compute_date_alert_stop',
        store=True, help="This date mention the date when"
        " the 'alert' state stops and when the partner will be suspended.")

    date_delay_stop = fields.Date(
        string='End Delay Date', compute='compute_date_delay_stop',
        store=True, help="This date mention the date when"
        " the 'delay' state stops and when the partner will be suspended.")

    extension_ids = fields.One2many(
        comodel_name='shift.extension', inverse_name='partner_id',
        string='Extensions')

    extension_qty = fields.Integer(
        string='Extensions Quantity', compute='compute_extension_qty',
        store=True)

    current_extension_day_end = fields.Char(
        string='Current Extension Day End', compute='compute_extension_qty',
    )

    counter_event_ids = fields.One2many(
        comodel_name='shift.counter.event', inverse_name='partner_id',
        string='Counter Events')

    default_addess_for_shifts = fields.Boolean(
        string="Use as default for Shifts")

    in_ftop_team = fields.Boolean(
        string="In FTOP Team",
        compute="_compute_in_ftop_team",
        store=False)

    # Constrains section
    @api.multi
    @api.constrains('display_std_points')
    def check_display_standard_point(self):
        '''
        @Constrains on field display_std_points
            - display_std_points must be <= 0
        '''
        for partner in self:
            if partner.display_std_points > 0:
                partner_name = '%s - %s' % (partner.barcode_base, partner.name)
                raise ValidationError(_(
                    "The member %s cannot accumulate more points " +
                    "on the standard counter. if you " +
                    "want this attendance to count, you " +
                    "need to change its type to FTOP.") % partner_name)

    # Compute section
    @api.multi
    @api.depends('leave_ids')
    def _compute_leave_qty(self):
        for partner in self:
            today = fields.Date.context_today(self)
            partner.leave_qty = len(partner.leave_ids.filtered(
                lambda l: l.stop_date >= today))
            current_leave = partner.leave_ids.filtered(
                lambda l: l.stop_date >= today and l.start_date <= today
                and l.state != 'cancel')
            if current_leave:
                partner.current_leave_info = "".join(
                    e[0].upper() for e in current_leave[0].type_id.name.split())\
                    + "-" + current_leave[0].stop_date.split('-')[2] + '/' +\
                    current_leave[0].stop_date.split('-')[1] + '/' +\
                    current_leave[0].stop_date.split('-')[0]
            else:
                partner.current_leave_info = False

    @api.multi
    def set_next_registration(self, next_registrations):
        self.ensure_one()
        num_abcd = 0
        ftop_next_registrations = next_registrations.filtered(
            lambda r: r.state == 'open' and
            r.shift_id.shift_type_id.is_ftop)
        if ftop_next_registrations:
            self.next_ftop_registration_date =\
                ftop_next_registrations[0].date_begin
        else:
            self.next_ftop_registration_date = False

        for registration in next_registrations.filtered(
            lambda r: r.state == 'open' and not
                r.shift_id.shift_type_id.is_ftop):
            if num_abcd < 4:
                self.next_abcd_registrations = [(4, registration.id)]
                num_abcd += 1

    @api.multi
    def _compute_registration_counts(self):
        d = fields.Datetime.now()
        for partner in self:
            next_registrations = partner.sudo().registration_ids.filtered(
                lambda r, d=d: r.date_begin >= d and not r.is_technical)

            # Set 4 next shifts
            partner.set_next_registration(next_registrations)

            partner.upcoming_registration_count = len(next_registrations)
            next_registrations = next_registrations.sorted(
                lambda r: r.date_begin)
            partner.next_registration_id = next_registrations and\
                next_registrations[0] or False
            partner.tmpl_registration_count = \
                len(partner.sudo().tmpl_reg_line_ids)
            partner.active_tmpl_reg_line_count = len(
                partner.sudo().tmpl_reg_line_ids.filtered(
                    lambda l: l.is_current or l.is_future))
            current_tmpl_reg_line = partner.tmpl_reg_line_ids.filtered(
                lambda l: l.is_current)
            if current_tmpl_reg_line:
                if not current_tmpl_reg_line[0].shift_template_id.shift_type_id.is_ftop:
                    partner.current_tmpl_reg_line =\
                        current_tmpl_reg_line[0].shift_template_id.name
                else:
                    partner.current_tmpl_reg_line =\
                        current_tmpl_reg_line[0].shift_template_id.name[:14]

    @api.multi
    def _compute_current_template_name(self):
        for partner in self:
            reg = partner.tmpl_reg_ids.filtered(
                lambda r: r.is_current)
            if reg:
                partner.current_template_name = reg[0].shift_template_id.name
            else:
                reg = partner.tmpl_reg_ids.filtered(
                    lambda r: r.is_future)
                if reg:
                    partner.current_template_name =\
                        reg[0].shift_template_id.name

    @api.multi
    def _compute_is_squadleader(self):
        for partner in self:
            partner.is_squadleader = False
            shifts = self.env['shift.shift'].search([
                ('user_ids', 'in', partner.id),
                ('date_begin', '>=', fields.Date.today())
            ])
            if len(shifts):
                partner.is_squadleader = True

    @api.depends('extension_ids.partner_id')
    @api.multi
    def compute_extension_qty(self):
        for partner in self:
            partner.extension_qty = len(partner.sudo().extension_ids)
            today = fields.Date.context_today(self)
            current_extension = partner.extension_ids.filtered(
                lambda e: e.date_start <= today and e.date_stop >= today)
            if current_extension:
                partner.current_extension_day_end =\
                    current_extension[0].date_stop.split('-')[2] + '/' +\
                    current_extension[0].date_stop.split('-')[1] + '/' +\
                    current_extension[0].date_stop.split('-')[0]
            else:
                partner.current_extension_day_end = False

    @api.depends('counter_event_ids', 'counter_event_ids.point_qty',
                 'counter_event_ids.type', 'counter_event_ids.partner_id',
                 'counter_event_ids.ignored')
    @api.multi
    def compute_final_standard_point(self):
        for partner in self:
            partner.final_standard_point = sum(
                [point_counter.point_qty
                    for point_counter in partner.counter_event_ids
                    if point_counter.type == 'standard' and
                 not point_counter.ignored])

    @api.depends('counter_event_ids', 'counter_event_ids.point_qty',
                 'counter_event_ids.type', 'counter_event_ids.partner_id',
                 'counter_event_ids.ignored')
    @api.multi
    def compute_final_ftop_point(self):
        for partner in self:
            partner.final_ftop_point = sum(
                [point_counter.point_qty
                    for point_counter in partner.counter_event_ids
                    if point_counter.type == 'ftop' and
                 not point_counter.ignored])

    @api.depends('counter_event_ids', 'counter_event_ids.point_qty',
                 'counter_event_ids.type', 'counter_event_ids.partner_id')
    def compute_display_counter_point(self):
        '''
        @Function to compute the actual current point for the member's status
        computation
        '''
        for partner in self:
            partner.display_std_points = \
                sum([point_counter.point_qty
                     for point_counter in partner.counter_event_ids
                     if point_counter.type == 'standard'])

            partner.display_ftop_points = \
                sum([point_counter.point_qty
                     for point_counter in partner.counter_event_ids
                     if point_counter.type == 'ftop'])

    def _compute_is_vacation(self):
        for partner in self:
            conflict = False
            for leave in partner.leave_ids.filtered(
                    lambda l: l.partner_state == 'vacation' and
                    l.state == 'done'):
                conflict = conflict or conflict_period(
                    leave.start_date, leave.stop_date,
                    fields.Date.context_today(self),
                    fields.Date.context_today(self), True)['conflict']
            partner.is_vacation = conflict

    def _compute_is_exempted(self):
        for partner in self:
            conflict = False
            for leave in partner.leave_ids.filtered(
                    lambda l: l.partner_state == 'exempted' and
                    l.state == 'done'):
                conflict = conflict or conflict_period(
                    leave.start_date, leave.stop_date,
                    fields.Date.context_today(self),
                    fields.Date.context_today(self), True)['conflict']
            partner.is_exempted = conflict

    @api.depends(
        'extension_ids.date_start', 'extension_ids.date_stop',
        'extension_ids.partner_id')
    def compute_date_delay_stop(self):
        """This function should be called in a daily CRON"""
        for partner in self:
            max_date = False
            for extension in partner.sudo().extension_ids:
                if extension.date_start <= fields.Datetime.now() and\
                        extension.date_stop > fields.Datetime.now():
                    max_date = max(max_date, extension.date_stop)
            if partner.date_delay_stop or max_date:
                partner.date_delay_stop = max_date

    @api.depends('final_standard_point', 'final_ftop_point')
    def compute_date_alert_stop(self):
        """This function should be called in a daily CRON"""
        alert_duration = int(self.env['ir.config_parameter'].sudo().get_param(
            'coop.shift.state.delay.duration'))
        # Read the current value of Date alert stop using read method as
        # partner.date_alert_stop will not work in a compute function
        current_partner_alert_date = {
            d['id']: d['date_alert_stop']
            for d in self.search_read(
                [('id', 'in', self.ids)],
                ['date_alert_stop'])
        }
        for partner in self:
            # If all is OK, the date is deleted
            point = 0
            if partner.in_ftop_team:
                point = partner.final_ftop_point
            else:
                point = partner.final_standard_point

            if point >= 0:
                partner.date_alert_stop = False
            elif not current_partner_alert_date.get(partner.id):
                partner.date_alert_stop =\
                    datetime.today() + relativedelta(days=alert_duration)
                partner.date_alert_stop = partner.date_alert_stop

    @api.model
    def compute_working_state_manually(self, member_ids):
        """
        This is util function which call by Cron with passing member_ids
        as arguments.
        It helps to test _compute_working_state function easily
        """
        self.browse(member_ids)._compute_working_state()

    @api.depends(
        'is_blocked', 'final_standard_point',
        'final_ftop_point', 'shift_type', 'date_alert_stop',
        'date_delay_stop', 'leave_ids.state')
    @api.multi
    def _compute_working_state(self):
        """This function should be called in a daily CRON"""
        current_datetime = fields.Datetime.now()
        for partner in self:
            state = 'up_to_date'
            if partner.is_blocked:
                state = 'blocked'
            elif partner.is_vacation:
                state = 'vacation'
            else:
                point = 0
                if partner.in_ftop_team:
                    point = partner.final_ftop_point
                else:
                    point = partner.final_standard_point

                if point < 0:
                    if partner.date_alert_stop:
                        if partner.date_delay_stop > current_datetime:
                            # There is Delay
                            state = 'delay'
                        elif partner.date_alert_stop > current_datetime:
                            # Grace State
                            state = 'alert'
                        else:
                            state = 'suspended'
                    else:
                        state = 'suspended'
                elif partner.is_exempted:
                    state = 'exempted'
            # Change the status from Up to Date
            # to Alert if standard_counter < 0
            if state == 'up_to_date' and partner.final_standard_point < 0:
                state = 'alert'
            if partner.working_state != state:
                partner.working_state = state

    @api.multi
    def _compute_in_ftop_team(self):
        ftop_type_ids = self.env['shift.type'].sudo().search(
            [('is_ftop', '=', True)]).ids
        for partner in self:
            tmpl_reg = partner.tmpl_reg_ids.filtered(
                lambda r: r.is_current
                and r.shift_ticket_id.shift_type == 'ftop'
                and r.shift_template_id.shift_type_id.id in ftop_type_ids
            )
            partner.in_ftop_team = len(tmpl_reg) > 0

    @api.depends('working_state')
    @api.multi
    def _compute_cooperative_state(self):
        """Overwrite me in a custom module, to add extra state"""
        for partner in self:
            partner.cooperative_state = partner.working_state

    # Custom Section
    @api.model
    def update_working_state(self):
        # Function Called by the CRON
        partners = self.search([])

        # Creating Jobs for updating the member working status
        # Split member list in multiple parts
        partner_ids = partners.ids
        num_partner_per_job = 200
        splited_partner_list = \
            [partner_ids[i: i + num_partner_per_job]
             for i in range(0, len(partner_ids), num_partner_per_job)]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid,
                                   context=self.env.context)
        # Create jobs
        for partner_list in splited_partner_list:
            update_member_working_state.delay(
                session, 'res.partner', partner_list)

    @api.multi
    def write(self, vals):
        if 'default_addess_for_shifts' in vals:
            for record in self:
                if record.parent_id:
                    if vals.get('default_addess_for_shifts'):
                        for child in record.parent_id.child_ids:
                            if child.id != record.id:
                                child.write({
                                    'default_addess_for_shifts': False
                                })

        return super(ResPartner, self).write(vals)


@job
def update_member_working_state(session, model_name, partner_ids):
    ''' Job for Updating Member Working State '''
    partners = session.env[model_name].browse(partner_ids)
    partners.compute_date_alert_stop()
    partners.compute_date_delay_stop()
    partners._compute_working_state()
