# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

from .date_tools import conflict_period


class ShiftLeaveWizard(models.TransientModel):
    _name = 'shift.leave.wizard'

    # Default Section
    @api.model
    def _default_leave_id(self):
        return self.env.context.get('active_id', False)

    @api.model
    def _default_shift_template_registration_line_ids(self):
        line_ids = []
        leave_id = self.env.context.get('active_id', False)
        if leave_id:
            leave = self.env['shift.leave'].browse(leave_id)
            for line in leave.partner_id.tmpl_reg_line_ids:
                if conflict_period(
                        leave.start_date, leave.stop_date,
                        line.date_begin, line.date_end)['conflict']:
                    line_ids.append(line.id)
        return line_ids

    @api.model
    def _default_shift_registration_ids(self):
        registration_ids = []
        leave_id = self.env.context.get('active_id', False)
        if leave_id:
            leave = self.env['shift.leave'].browse(leave_id)
            for registration in leave.partner_id.registration_ids:
                if conflict_period(
                        leave.start_date, leave.stop_date,
                        registration.date_begin,
                        registration.date_end)['conflict']:
                    registration_ids.append(registration.id)
        return registration_ids

    # Column Section
    leave_id = fields.Many2one(
        string='Leave', required=True, comodel_name='shift.leave',
        default=_default_leave_id, readonly=True)

    type_id = fields.Many2one(
        comodel_name='shift.leave.type', string='Type',
        related='leave_id.type_id', readonly=True)

    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner',
        related='leave_id.partner_id', readonly=True)

    start_date = fields.Date(
        string='Begin Date', related='leave_id.start_date', readonly=True)

    stop_date = fields.Date(
        string='Stop Date', related='leave_id.start_date', readonly=True)

    shift_template_registration_line_ids = fields.Many2many(
        comodel_name='shift.template.registration.line', readonly=True,
        string='Template Attendees',
        default=_default_shift_template_registration_line_ids)

    shift_registration_ids = fields.Many2many(
        comodel_name='shift.registration', readonly=True,
        string='Attendees',
        default=_default_shift_registration_ids)

    # View Section
    @api.multi
    def button_confirm(self):
        self.ensure_one()
        if self.leave_id.state != 'draft':
                raise ValidationError(_(
                    "You can not confirm a leave in a non draft state."))
        for registration in self.shift_registration_ids:
            if registration.state != 'cancel':
                registration.button_reg_cancel()
        self.leave_id.state = 'done'
