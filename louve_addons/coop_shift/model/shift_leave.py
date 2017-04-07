# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

from .shift_leave_type import LEAVE_TYPE_STATE_SELECTION
from .date_tools import conflict_period


class ShiftLeave(models.Model):
    _name = 'shift.leave'
    _order = 'start_date desc, partner_id asc'

    LEAVE_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ]

    name = fields.Char(
        string='Name', compute='_compute_name', store=True, select=True)

    type_id = fields.Many2one(
        comodel_name='shift.leave.type', string='Type', required=True,
        select=True, readonly=True, states={'draft': [('readonly', False)]})

    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner', required=True,
        select=True, readonly=True, states={'draft': [('readonly', False)]})

    start_date = fields.Date(
        string='Begin Date', required=True,
        readonly=True, states={'draft': [('readonly', False)]})

    stop_date = fields.Date(
        string='Stop Date', readonly=True,
        states={'draft': [('readonly', False)]},
        help="Last day of the period, during wich the partner is not"
        " available to work.")

    state = fields.Selection(
        selection=LEAVE_STATE_SELECTION, default='draft')

    partner_state = fields.Selection(
        selection=LEAVE_TYPE_STATE_SELECTION, related='type_id.state',
        readonly=True, store=True, help=" State"
        " of the people during the leave.\n * 'Exempted' : The customer"
        " can buy.\n * 'On vacation' : The customer can not buy.")

    other_leave_ids = fields.One2many(
        comodel_name='shift.leave', string='Leaves',
        compute='_compute_other_leave_ids')

    duration = fields.Integer(
        string='Duration', compute='_compute_duration', store=True,
        help="Duration (in Days)")

    require_stop_date = fields.Boolean(
        string='Required Stop Date', related='type_id.require_stop_date')

    shift_template_registration_line_ids = fields.One2many(
        'shift.template.registration.line', 'leave_id')

    # Compute Section
    @api.depends('start_date', 'stop_date')
    def _compute_duration(self):
        for leave in self:
            if not (leave.start_date and leave.stop_date):
                leave.duration = False
            else:
                start_date = datetime.strptime(
                    leave.start_date, DEFAULT_SERVER_DATE_FORMAT)
                stop_date = datetime.strptime(
                    leave.stop_date, DEFAULT_SERVER_DATE_FORMAT)
                leave.duration = (stop_date - start_date).days + 1

    @api.depends('partner_id', 'type_id')
    def _compute_name(self):
        for leave in self:
            if leave.partner_id and leave.type_id:
                leave.name = '%s - %s' % (
                    leave.type_id.name, leave.partner_id.name)
            else:
                leave.name = ''

    @api.depends('partner_id.leave_ids')
    def _compute_other_leave_ids(self):
        for leave in self:
            leave.other_leave_ids = list(
                set(leave.partner_id.leave_ids.ids) - set([leave.id]))

    # constraints Section
    @api.multi
    @api.constrains('start_date', 'stop_date')
    def _check_dates(self):
        for leave in self:
            if leave.stop_date and leave.stop_date < leave.start_date:
                raise ValidationError(_(
                    "Stop Date should be greater than Start Date."))

    @api.multi
    @api.constrains('start_date', 'stop_date', 'partner_id', 'state')
    def _check_partner_leaves(self):
        for leave in self:
            if leave.state == 'cancel':
                continue
            for other_leave in leave.other_leave_ids.filtered(
                    lambda r: r.state != 'cancel'):
                if conflict_period(
                        leave.start_date, leave.stop_date,
                        other_leave.start_date, other_leave.stop_date)[
                            'conflict']:
                    raise ValidationError(_(
                        "The partner has an incompatible draft of done leave\n"
                        " * start date : %s\n * stop date : %s\n") % (
                            other_leave.start_date,
                            other_leave.stop_date and other_leave.stop_date or
                            _('Undefined')))

    # Overload Section
    @api.multi
    def copy(self, default=None):
        raise ValidationError(_(
            "You can not duplicate a leave : Unimplemented Feature"))

    @api.multi
    def unlink(self):
        for leave in self:
            if leave.state == 'done':
                raise ValidationError(_(
                    "You can not unlink leaves in a done state."))
        return super(ShiftLeave, self).unlink()

    @api.multi
    def button_cancel(self):
        for leave in self:
            if leave.state == 'done':
                leave.shift_template_registration_line_ids.write(
                    {'state': 'open'})
                leave.state = 'cancel'
                leave.shift_template_registration_line_ids = False

    @api.multi
    def button_draft(self):
        for leave in self:
            if leave.state == 'cancel':
                leave.state = 'draft'
