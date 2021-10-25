# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class ShiftExtension(models.Model):
    _inherit = 'shift.extension'
    _order = 'date_start desc, partner_id'

    reduce_deduction = fields.Boolean(string="Reduced Deduction")
    is_show_reduce_deduction = fields.Boolean(
        compute="_compute_show_reduce_deduction",
        string="Is Show Reduced Deduction",
        store=True)
    current_extension = fields.Boolean(compute='_compute_current_extension',
                                       store=False)

    @api.onchange('type_id', 'partner_id', 'date_start')
    def onchange_type_id(self):
        '''
        @Function to suggest the end date for the member
        '''
        for extension in self:
            extension.date_stop = self.suggest_extension_date_stop(
                extension_type=extension.type_id,
                partner=extension.partner_id,
                date_start=extension.date_start)

    @api.depends('date_start', 'date_stop')
    def _compute_current_extension(self):
        today_date = date.today()
        for ext in self:
            if ext.date_start <= today_date and ext.date_stop >= today_date:
                ext.current_extension = True
            else:
                ext.current_extension = False

    @api.multi
    @api.depends('partner_id.shift_type', 'type_id.extension_method')
    def _compute_show_reduce_deduction(self):
        for record in self:
            # important, it reads from the database
            record.partner_id.read(['shift_type'])
            if record.type_id.extension_method \
                == 'to_next_regular_shift' and \
                    record.partner_id.shift_type == 'ftop':
                record.is_show_reduce_deduction = True
            else:
                record.is_show_reduce_deduction = False

    @api.model
    def suggest_extension_date_stop(self, extension_type, partner, date_start):
        '''
        @Function to suggest the date stop for the extensions
        '''
        date_stop = False
        if extension_type and date_start:
            if extension_type.extension_method == 'fixed_duration':
                date_start = fields.Date.from_string(date_start)
                date_stop = date_start + \
                    relativedelta(days=extension_type.duration)
            elif partner and extension_type.extension_method == \
                    'to_next_regular_shift':
                # Get next shift date
                _next_shift_time, next_shift_date = \
                    partner.get_next_shift_date()
                date_stop = next_shift_date
        return date_stop

    @api.model
    def create(self, vals):
        res = super(ShiftExtension, self).create(vals)
        if res.reduce_deduction:
            res._validate_reduced_deduction()
        return res

    @api.multi
    def _validate_reduced_deduction(self):
        '''
            This method check the extension for calculating point of partner
        '''
        for record in self:

            date_stop = fields.Datetime.now()

            shift_registration_env = self.env['shift.registration']

            shift_regs = shift_registration_env.search([
                ('partner_id', '=', record.partner_id.id),
                ('template_created', '=', True),
                ('date_begin', '>=', record.date_start),
            ])
            shift_regs = shift_regs.filtered(
                lambda s: s.shift_id.state != 'done').sorted(
                key=lambda shift: shift.date_begin)
            if shift_regs:
                date_stop = shift_regs[0].date_begin

            # next_shift_date = record.partner_id.get_next_shift_date(
            #     record.date_start)
            past_reduced_attendees = \
                record.partner_id.registration_ids.filtered(
                    lambda r: r.date_begin < date_stop and
                    r.shift_id.shift_type_id.is_ftop).sorted(
                    key=lambda r: r.date_begin, reverse=True)

            attendees = self.env['shift.registration']
            for attendee in past_reduced_attendees:
                if len(attendees) >= 2:
                    break
                attendees = attendees | attendee

            # The vacation point must be less than 1 and the
            # partners can't benifit consecutive over 2 time
            if record.partner_id.display_ftop_points >= 1:
                raise ValidationError(_(
                    "The counter of the member is positive."))
            elif len(attendees) == 2 and not any(
                    not attendee.reduce_extension_id.reduce_deduction
                    for attendee in attendees):
                raise ValidationError(_(
                    "Impossible. The member has already benefited from 2" +
                    " consecutive reduced counts."))
            elif shift_regs:
                shift_regs[0].reduce_extension_id = record.id

    @api.multi
    def write(self, vals):
        res = super(ShiftExtension, self).write(vals)
        for record in self:
            if record.reduce_deduction:
                record._validate_reduced_deduction()
        return res
