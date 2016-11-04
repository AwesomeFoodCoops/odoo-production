# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Cyril Gaspard
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Julien WESTE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    SHIFT_TYPE_SELECTION = [
        ('standard', 'Standard'),
        ('ftop', 'FTOP'),
    ]

    WORKING_STATE_SELECTION = [
        ('up_to_date', 'Up to date'),
        ('alert', 'Alert'),
        ('suspended', 'Suspended'),
        ('delay', 'Delay'),
        ('blocked', 'Blocked'),
    ]

    is_blocked = fields.Boolean(
        string='Blocked', help="Check this box to manually block this user.")

    shift_type = fields.Selection(
        selection=SHIFT_TYPE_SELECTION, string='Shift type', required=True,
        default='standard')

    working_state = fields.Selection(
        selection=WORKING_STATE_SELECTION, string='Working State', store=True,
        compute='_compute_working_state', help="This state depends on the"
        " shifts realized by the partner.")

    cooperative_state = fields.Selection(
        selection=WORKING_STATE_SELECTION, string='Cooperative State',
        store=True, compute='_compute_cooperative_state', help="This state"
        " depends on the 'Working State' and extra custom settings.")

    theoritical_standard_point = fields.Integer(
        string='theoritical Standard points', store=True,
        compute='compute_theoritical_standard_point')

    manual_standard_correction = fields.Integer(
        string='Manual Standard Correction')

    final_standard_point = fields.Integer(
        string='Final Standard points', compute='compute_final_standard_point',
        store=True)

    theoritical_ftop_point = fields.Integer(
        string='theoritical FTOP points', store=True,
        compute='compute_theoritical_ftop_point')

    manual_ftop_correction = fields.Integer(
        string='Manual FTOP Correction')

    final_ftop_point = fields.Integer(
        string='Final FTOP points', compute='compute_final_ftop_point',
        store=True)

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

    # Compute Section
    @api.depends('extension_ids.partner_id')
    @api.multi
    def compute_extension_qty(self):
        for partner in self:
            partner.extension_qty = len(partner.extension_ids)

    @api.depends('theoritical_standard_point', 'manual_standard_correction')
    @api.multi
    def compute_final_standard_point(self):
        for partner in self:
            partner.final_standard_point =\
                partner.theoritical_standard_point +\
                partner.manual_standard_correction

    @api.depends('theoritical_ftop_point', 'manual_ftop_correction')
    @api.multi
    def compute_final_ftop_point(self):
        for partner in self:
            partner.final_ftop_point =\
                partner.theoritical_ftop_point +\
                partner.manual_ftop_correction

    @api.depends(
        'registration_ids.state', 'registration_ids.shift_type')
    @api.multi
    def compute_theoritical_standard_point(self):
        for partner in self:
            point = 0
            for registration in partner.registration_ids.filtered(
                        lambda reg: reg.shift_type == 'standard'):
                if not registration.template_created:
                    if registration.state in ['done', 'replaced']:
                        point += +1
                # In all cases
                if registration.state in ['absent']:
                    point += -2
                elif registration.state in ['excused']:
                    point += -1
                # if 'waiting' state, point is not impacted
            partner.theoritical_standard_point = point

    @api.depends('registration_ids.state', 'registration_ids.shift_type')
    @api.multi
    def compute_theoritical_ftop_point(self):
        for partner in self:
            point = 0
            for registration in partner.registration_ids.filtered(
                        lambda reg: reg.shift_type == 'ftop'):
                if registration.template_created:
                    # The presence was forecasted
                    if registration.state in ['absent', 'excused', 'waiting']:
                        point += -1
                else:
                    if registration.state in ['absent']:
                        point += -1
                    elif registration.state in ['present']:
                        point += 1
            partner.theoritical_ftop_point = point

    @api.depends(
        'extension_ids.date_start', 'extension_ids.date_stop',
        'extension_ids.partner_id')
    @api.multi
    def compute_date_delay_stop(self):
        """This function should be called in a daily CRON"""
        for partner in self:
            max_date = False
            for extension in partner.extension_ids:
                if extension.date_start <= fields.Datetime.now() and\
                        extension.date_stop > fields.Datetime.now():
                    max_date = max(max_date, extension.date_stop)
            partner.date_delay_stop = max_date

    @api.depends('final_standard_point', 'final_ftop_point')
    @api.multi
    def compute_date_alert_stop(self):
        """This function should be called in a daily CRON"""
        alert_duration = int(self.env['ir.config_parameter'].sudo().get_param(
            'coop.shift.state.delay.duration'))
        for partner in self:
            # If all is OK, the date is deleted
            point = partner.shift_type == 'standard'\
                and partner.final_standard_point\
                or partner.final_ftop_point
            if point > 0:
                partner.date_alert_stop = False
            elif not partner.date_alert_stop:
                partner.date_alert_stop =\
                    datetime.today() + relativedelta(days=alert_duration)
                partner.date_alert_stop = partner.date_alert_stop

    @api.depends(
        'is_blocked', 'final_standard_point', 'final_ftop_point',
        'shift_type', 'date_alert_stop', 'date_delay_stop')
    @api.multi
    def _compute_working_state(self):
        """This function should be called in a daily CRON"""
        for partner in self:
            state = 'up_to_date'
            if partner.is_blocked:
                state = 'blocked'
            else:
                point = partner.shift_type == 'standard'\
                    and partner.final_standard_point\
                    or partner.final_ftop_point
                if point < 0:
                    if partner.date_alert_stop:
                        if partner.date_delay_stop > fields.Datetime.now():
                            # There is Delay
                            state = 'delay'
                        elif partner.date_alert_stop > fields.Datetime.now():
                            # Grace State
                            state = 'alert'
                        else:
                            state = 'suspended'
                    else:
                        state = 'suspended'
            partner.working_state = state

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
        partners.compute_date_alert_stop()
        partners.compute_date_delay_stop()
