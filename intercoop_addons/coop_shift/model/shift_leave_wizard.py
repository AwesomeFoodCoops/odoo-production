# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

from .date_tools import conflict_period, add_days


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
                        line.date_begin, line.date_end, True)['conflict']:
                    line_ids.append(line.id)
        return line_ids

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
        string='Stop Date', related='leave_id.stop_date', readonly=True)

    shift_template_registration_line_ids = fields.Many2many(
        comodel_name='shift.template.registration.line', readonly=True,
        string='Template Attendees',
        default=_default_shift_template_registration_line_ids)

    # View Section
    @api.multi
    def button_confirm(self):
        self.ensure_one()

        leave = self.leave_id
        if not self._context.get('bypass_non_draft_confirm', False) and \
                leave.state != 'draft':
            raise ValidationError(_(
                "You can not confirm a leave in a non draft state."))

        registration_ids = self.shift_template_registration_line_ids\
            .mapped('registration_id').ids
        leave_s_date = leave.start_date
        leave_e_date = leave.stop_date

        for line in self.shift_template_registration_line_ids:
            previous_date_end = line.date_end
            work_s_date = line.date_begin
            work_e_date = line.date_end

            # if same period, delete registration line
            if work_s_date == leave_s_date and work_e_date == leave_e_date:
                # We confirm the same leave, previously canceled
                line.unlink()
            elif leave_s_date >= work_s_date:
                # Otherwise, Reduce current registration line stop date
                if leave_s_date > work_s_date:
                    line.date_end = add_days(leave_s_date, -1)
                else:
                    line.date_end = leave_e_date

                if leave_e_date and (not previous_date_end or
                                     previous_date_end > leave_e_date):
                    # Create a new registration line, if leave has stop date
                    line.copy(default={
                        'date_begin': add_days(leave_e_date, 1),
                        'date_end': previous_date_end,
                    })
            elif leave_e_date and work_e_date and work_e_date <= leave_e_date:
                line.unlink()
            else:
                line.date_begin = add_days(leave_e_date, 1)

        line_obj = self.env['shift.template.registration.line']
        for registration_id in registration_ids:
            # Update state of existing registration lines
            existed_line = line_obj.search([
                ('registration_id', '=', registration_id),
                ('date_begin', '=', leave_s_date),
                ('state', '!=', 'waiting'),
            ])
            if existed_line:
                existed_line.with_context(bypass_leave_change_check=True)\
                    .write({'state': 'waiting', 'leave_id': leave.id})
            else:
                # Create new registration lines (type 'waiting')
                line_obj.create({
                    'registration_id': registration_id,
                    'date_begin': leave_s_date,
                    'date_end': leave_e_date,
                    'state': 'waiting',
                    'leave_id': leave.id,
                })

        leave.state = 'done'
