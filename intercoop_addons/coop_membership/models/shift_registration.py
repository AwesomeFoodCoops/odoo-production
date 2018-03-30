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

from openerp import api, models, fields, _
from openerp.exceptions import UserError
from datetime import datetime
import pytz


class ShiftRegistration(models.Model):
    _inherit = 'shift.registration'

    partner_id = fields.Many2one(
        domain=[('is_worker_member', '=', True)])

    related_extension_id = fields.Many2one('shift.extension',
                                           string="Related Shift Extensions")

    related_shift_state = fields.Selection(related="shift_id.state",
                                           store=False,
                                           string="Shift State")

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id', False)
        partner = self.env['res.partner'].browse(partner_id)
        if partner.is_unsubscribed and not self.env.context.get(
                'creation_in_progress', False):
            raise UserError(_(
                """You can't register this partner on a shift because """
                """he isn't registered on a template"""))
        res = super(ShiftRegistration, self).create(vals)
        # Do not allow member with Up to date status register make up
        # in a ABCD shift on a ABCD tickets
        res.checking_shift_attendance()

        # Don't allow member register in leaving time
        res.check_leave_time()
        return res

    @api.multi
    def action_create_extension(self):
        """
        @Function triggered by a button on Attendance tree view
        to create extension automatically for a member:
            - Extension Type: Extension
            - Start Date: registration start date
            - End Date: Next Shift Date
        """
        shift_extension_env = self.env['shift.extension']
        for registration in self:
            partner = registration.partner_id
            extension_type = self.env.ref(
                'coop_membership.shift_extension_type_extension')

            date_begin_obj = datetime.strptime(
                fields.Datetime.now(), '%Y-%m-%d %H:%M:%S')
            tz_name = self._context.get('tz') or self.env.user.tz
            utc_timestamp = pytz.utc.localize(
                date_begin_obj, is_dst=False)
            context_tz = pytz.timezone(tz_name)
            date_begin_object_tz = utc_timestamp.astimezone(context_tz)
            date_begin_date = date_begin_object_tz.strftime('%Y-%m-%d')

            ext_vals = {
                'partner_id': partner.id,
                'type_id': extension_type.id,
                'date_start': date_begin_date,
                'date_stop': shift_extension_env.suggest_extension_date_stop(
                    extension_type=extension_type,
                    partner=partner,
                    date_start=date_begin_date)
            }
            res_extension = shift_extension_env.create(ext_vals)
            registration.related_extension_id = res_extension.id

    @api.multi
    def button_reg_absent(self):
        res = super(ShiftRegistration, self).button_reg_absent()
        for reg in self:
            # Terminate the shift member
            if reg.template_created and reg.shift_type == 'standard':
                # Check for his next last shift registration
                last_shift_reg = self.search(
                    [('partner_id', '=', reg.partner_id.id),
                     ('template_created', '=', True),
                     ('date_begin', '<', reg.date_begin),
                     ('shift_type', '=', 'standard')],
                    order='date_begin desc', limit=1)
                if last_shift_reg and last_shift_reg.state == 'absent':
                    # Check for any standard shift within
                    markup_shift_reg_count = self.search_count(
                        [('partner_id', '=', reg.partner_id.id),
                         ('date_begin', '>', last_shift_reg.date_begin),
                         ('date_begin', '<', reg.date_begin),
                         ('shift_type', '=', 'standard'),
                         ('state', 'in', ('done', 'replaced'))])
                    # If no markup reg found, set date end for the reg shift
                    if not markup_shift_reg_count:
                        tz_name = self._context.get('tz') or self.env.user.tz
                        date_end_obj = datetime.strptime(
                            reg.date_end, '%Y-%m-%d %H:%M:%S')
                        utc_timestamp = pytz.utc.localize(
                            date_end_obj, is_dst=False)
                        context_tz = pytz.timezone(tz_name)
                        reg_date_end_tz = utc_timestamp.astimezone(context_tz)

                        final_date_end = reg_date_end_tz.strftime('%Y-%m-%d')
                        reg.tmpl_reg_line_id.date_end = final_date_end

                        # Sending the email to notify the member
                        partner = reg.partner_id

                        # Get the template xml from context
                        template_name = self.env.context.get(
                            "unsubscribe_email_template", False)
                        if not template_name:
                            template_name = "coop_membership.unsubscribe_email"
                        mail_template = \
                            self.env.ref(template_name)
                        if not mail_template:
                            continue
                        mail_template.send_mail(partner.id)
        return res

    @api.multi
    def write(self, vals):
        """
        Overide write function to update point counter for member
            + Standard:
                Add 1: Status is Attended / Replaced and template not created
                Deduct 2: Status is Absent
                Deduct 1: Status is Excused
            + FTOP
                Add 1: Status is Attended / Replaced
                Deduct 1: Status is Excused / Waiting and template created
                Deduct 1: Status is Absent
        """
        point_counter_env = self.env['shift.counter.event']
        vals_state = vals.get('state')
        for shift_reg in self:
            if vals_state != shift_reg.state:
                counter_vals = {}
                if shift_reg.shift_type == 'ftop':
                    if vals_state in ['done', 'replaced']:
                        reason = vals_state == 'done' and \
                            _('Attended') or \
                            _('Replaced')
                        counter_vals['point_qty'] = 1
                        counter_vals['name'] = reason

                    elif vals_state in ['absent']:
                        counter_vals['point_qty'] = -1
                        counter_vals['name'] = _('Absent')

                        # Mark the point as ignored if the member is in
                        # ftop team and not belong to this team
                        if not shift_reg.tmpl_reg_line_id and \
                                shift_reg.partner_id.in_ftop_team:
                            counter_vals['ignored'] = True

                    elif vals_state in ['excused', 'waiting'] and \
                            shift_reg.template_created:
                        reason = vals_state == 'excused' and \
                            _('Excused') or \
                            _('Waiting')
                        counter_vals['point_qty'] = -1
                        counter_vals['name'] = reason

                elif shift_reg.shift_type == 'standard':
                    # Check if a member is belong to the template
                    if shift_reg.template_created:
                        if vals_state in ['absent']:
                            counter_vals['point_qty'] = -2
                            counter_vals['name'] = _('Absent')

                        elif vals_state in ['excused']:
                            counter_vals['point_qty'] = -1
                            counter_vals['name'] = _('Excused')
                    else:
                        if vals_state in ['done', 'replaced']:
                            reason = _('Attended')
                            counter_vals['point_qty'] = 1
                            counter_vals['name'] = reason

                # Create Point Counter
                if counter_vals:
                    counter_vals.update({
                        'shift_id': shift_reg.shift_id.id,
                        'type': shift_reg.shift_type,
                        'partner_id': shift_reg.partner_id.id,
                    })

                    point_counter_env.sudo().with_context(
                        automatic=True).create(counter_vals)

        res = super(ShiftRegistration, self).write(vals)
        if 'template_created' in vals or 'shift_ticket_id' in vals:
            self.checking_shift_attendance()

        if 'template_created' in vals or 'shift_ticket_id' in vals or 'shift_id' in vals:
            self.check_leave_time()
        return res

    @api.multi
    @api.onchange("shift_id")
    def onchange_shift_id(self):
        # Use the context value for default
        is_standard_ticket = self.env.context.get("is_standard_ticket", False)
        ticket_type_product = False
        if is_standard_ticket:
            ticket_type_product = \
                self.env.ref("coop_shift.product_product_shift_standard")
        else:
            ticket_type_product = \
                self.env.ref("coop_shift.product_product_shift_ftop")
        for reg in self:
            reg.shift_ticket_id = reg.shift_id.shift_ticket_ids.filtered(
                lambda t: t.product_id == ticket_type_product)

    @api.multi
    def checking_shift_attendance(self):
        """
        @Function to check the attendance:
            - Do not allow member with Up to date status registers make up
            in a ABCD shift on a ABCD tickets
        """
        ignore_checking = \
            self.env.context.get('ignore_checking_attendance', False)
        if ignore_checking:
            return
        uptodate_list = []
        for shift_reg in self:
            shift_type = shift_reg.shift_id and \
                shift_reg.shift_id.shift_type_id
            if shift_type and not shift_type.is_ftop and \
                    shift_reg.shift_type == 'standard' and \
                    not shift_reg.template_created and \
                    shift_reg.state not in ['replacing', 'replaced'] and \
                    shift_reg.partner_id.working_state == 'up_to_date':
                uptodate_list.append('- [%s] %s' % (
                    shift_reg.partner_id.barcode_base,
                    shift_reg.partner_id.name))
        if uptodate_list:
            raise UserError(_("Warning! You cannot enter make-ups of " +
                              "the following members " +
                              "as they are up-to-date: \n\n%s") %
                            '\n'.join(uptodate_list))

    @api.multi
    def check_leave_time(self):
        """
        Check leaving time when register the shift
        Odoo should prevent them from scheduling shift that falls within the period of the leave
        """
        is_from_template = self._context.get('from_shift_template', False)
        for reg in self:
            # Get leave 
            leaves = reg.partner_id.leave_ids.filtered(
                lambda l: (l.type_id.is_temp_leave or l.type_id.is_incapacity)
                and l.stop_date and l.state == 'done')

            for leave in leaves:
                if reg.date_end >= leave.start_date and\
                        reg.date_begin <= leave.stop_date:
                    if reg.shift_id.shift_type_id.is_ftop:

                        # Check attendee be crated from template
                        if is_from_template:
                            reg.state = 'waiting'
                        else:
                            # Get list attendee
                            partner_tmp_ids = reg.shift_id.shift_template_id.\
                                registration_ids.mapped('partner_id').ids
                            # Check attendde already be in template
                            if reg.partner_id.id in partner_tmp_ids:
                                reg.state = 'waiting'
                            else:
                                raise UserError(_(
                                    "You can't register the shift (%s - %s) "
                                    "that falls within the period of the leave (%s - %s)" %
                                    (reg.date_begin, reg.date_end, leave.start_date,
                                     leave.stop_date)))
                    elif not reg.shift_id.shift_type_id.is_ftop and\
                            leave.type_id.is_temp_leave:

                        # Check attendee be crated from template
                        if is_from_template:
                            reg.state = 'waiting'
                        else:
                            # Get list attendee
                            partner_tmp_ids = reg.shift_id.shift_template_id.\
                                registration_ids.mapped('partner_id').ids
                            # Check attendde already be in template
                            if reg.partner_id.id in partner_tmp_ids:
                                reg.state = 'waiting'
                            else:
                                raise UserError(_(
                                    "You can't register the shift (%s - %s) "
                                    "that falls within the period of the leave (%s - %s)" %
                                    (reg.date_begin, reg.date_end, leave.start_date,
                                     leave.stop_date)))
