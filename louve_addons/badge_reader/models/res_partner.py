# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
import pytz
from datetime import datetime
from datetime import timedelta

BADGE_PARTNER_BOOTSTRAP_COOPERATIVE_STATE = [
    ('success', 'OK'),
    ('warning', 'Warning'),
    ('danger', 'Danger'),
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    MAPPING_COOPERATIVE_STATE = {
        'up_to_date': 'success',
        'alert': 'warning',
        'delay': 'warning',
        'suspended': 'danger',
        'not_concerned': 'danger',
        'blocked': 'danger',
        'unpayed': 'danger',
        'unsubscribed': 'danger',
    }

    next_shift_time = fields.Datetime(
        string="Next Shift Time",
        compute="compute_next_shift_time")

    bootstrap_cooperative_state = fields.Selection(
        compute='_compute_bootstrap_cooperative_state',
        string='Bootstrap State', store=True,
        selection=BADGE_PARTNER_BOOTSTRAP_COOPERATIVE_STATE)

    # Compute Section
    @api.depends('cooperative_state')
    @api.multi
    def _compute_bootstrap_cooperative_state(self):
        for partner in self:
            partner.bootstrap_cooperative_state =\
                self.MAPPING_COOPERATIVE_STATE.get(
                    partner.cooperative_state, 'danger')

    @api.multi
    def compute_next_shift_time(self):
        for partner in self:
            next_shift_time, _next_shift_date = partner.get_next_shift_date()
            partner.next_shift_time = next_shift_time

    # Custom Section
    @api.multi
    def log_move(self, action):
        self.ensure_one()
        partner_move_obj = self.env['res.partner.move']
        for partner in self:
            partner_move_obj.create({
                'partner_id': partner.id,
                'cooperative_state': partner.cooperative_state,
                'action': action,
                'bootstrap_cooperative_state':
                partner.bootstrap_cooperative_state,
            })

    @api.multi
    def action_grace_partner(self):
        '''
        @Function call when gracing a partner:
            Creating Extension for partner
                - Start Date: Current Date
                - End Date:
                    Current Date + Duration
                    If End Date exceeds the next Shift Time, End Date will
                    be the next shift time
        '''
        self.ensure_one()
        # Only grace extensions for suspended user with no extension
        if self.cooperative_state != 'suspended' or self.extension_ids:
            return False

        shift_ext_env = self.env['shift.extension']
        ext_type_env = self.env['shift.extension.type']
        date_start_str = fields.Date.context_today(self)
        grace_ext_type = ext_type_env.search([('is_grace_period', '=', True)],
                                             limit=1)

        if not grace_ext_type:
            return False

        # Create new extension
        date_stop = datetime.strptime(date_start_str, '%Y-%m-%d') + \
            timedelta(days=grace_ext_type.duration)
        date_stop_str = date_stop.strftime('%Y-%m-%d')

        # Check The Date Stop with the Shift Limitation
        _next_shift_time, next_shift_date = self.get_next_shift_date()

        if next_shift_date:
            # Set the next shift date as the end date if the end date exceed
            # the next shift date
            date_stop_str = date_stop_str > next_shift_date and \
                next_shift_date or date_stop_str

        # Create extension
        shift_ext_env.create({
            'date_start': date_start_str,
            'date_stop': date_stop_str,
            'partner_id': self.id,
            'type_id': grace_ext_type.id
        })
        return True

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
