# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from datetime import datetime, timedelta
from dateutil import rrule

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class ShiftChangeTeam(models.Model):
    _name = "shift.change.team"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", compute="_compute_name_change_team",
                       store="True")
    partner_id = fields.Many2one('res.partner', string="Member", required=True)
    current_shift_template_id = fields.Many2one(
        'shift.template',
        compute="compute_mess_change_team",
        string="Current Team",
        store=True)
    next_current_shift_date = fields.Date(
        compute="compute_mess_change_team",
        string='Next Shift with the Current Team',
        store=True)
    new_shift_template_id = fields.Many2one(
        'shift.template', string="New Team", required=True)
    is_abcd_to_abcd = fields.Boolean(
        compute="compute_mess_change_team",
        string="Is ABCD to ABCD ?",
        store=True,
        default=False)
    first_next_shift_date = fields.Date(
        string="The date of first shift in new team",
    )
    second_next_shift_date = fields.Date(
        string="The date of second shift in new team",
    )
    full_seats_mess = fields.Html(
        compute="compute_full_seats_massagess",
        string="Full Seats Messagess",
        store=True
    )
    is_full_seats_mess = fields.Boolean(
        compute="compute_full_seats_massagess",
        string="Show full seats warning",
        store=True)
    new_next_shift_date = fields.Date(
        string="Start Date with the New Team",
        required=True)
    mess_change_team = fields.Html(
        string='Message Change Team',
        compute='compute_mess_change_team',
        store=True)
    is_mess_change_team = fields.Boolean(
        compute="compute_mess_change_team",
        string="Show changing team messages",
        default=False,
        store=True)
    partner_state = fields.Selection([
        ('subscribed', 'Subscribed'), ('unsubscribed', 'Unsubscribed')],
        compute="compute_mess_change_team",
        string="Current Team",
        default='subscribed',
        store=True
    )
    show_partner_state = fields.Boolean(
        compute="compute_mess_change_team",
        string="Show partner state",
        default=False,
        store=True)
    is_catch_up = fields.Boolean(
        string="Add a catch-up?",
        default=False,
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('closed', 'Closed')],
        string="Status",
        default="draft",
    )

    @api.multi
    @api.depends('partner_id')
    def _compute_name_change_team(self):
        for record in self:
            msg = _('Changes Team')
            record.name = '%s %s' % (record.partner_id.name, msg)

    @api.multi
    @api.constrains('current_shift_template_id', 'new_shift_template_id')
    def change_team_constraints(self):
        for record in self:
            if record.current_shift_template_id ==\
                    record.new_shift_template_id:
                raise UserError(
                    _('The new team should be different the current team'))

    @api.multi
    def _send_notification_email(self):
        mail_template_abcd = self.env.ref(
            'coop_membership.change_team_abcd_email')
        mail_template_ftop = self.env.ref(
            'coop_membership.change_team_ftop_email')
        # Hack to add attachments to the ftop email template
        # It should really be added in a data xml.. don't know why it's here
        if not mail_template_ftop.attachment_ids:
            mail_template_ftop.attachment_ids = [(6, 0, [
                self.env.ref('coop_membership.volant_sheet_attachment').id,
                self.env.ref('coop_membership.volant_calendar_attachment').id,
            ])]
        for rec in self:
            if rec.new_shift_template_id.shift_type_id.is_ftop:
                mail_template_ftop.send_mail(rec.id)
            else:
                mail_template_abcd.send_mail(rec.id)

    @api.multi
    def button_close(self):
        for record in self:
            if not self.env.context.get('skip_sanity_checks'):
                if not record.partner_id.is_member:
                    raise UserError(_(
                        'A person you want to change team must be a member'))
                if record.is_mess_change_team or record.is_full_seats_mess:
                    raise UserError(_(
                        'There are some processes that were not done, '
                        'please do it!'))
            # Do actual change
            record.set_in_new_team()
            record.state = 'closed'
            # Handle Catch up mechanism
            if not record.new_shift_template_id.shift_type_id.is_ftop:
                if record.is_catch_up:
                    self.env['shift.counter.event'].sudo().with_context(
                        automatic=True,
                    ).create({
                        'name': _('Subtracted 1 point for changing team'),
                        'type': 'standard',
                        'partner_id': record.partner_id.id,
                        'point_qty': -1,
                    })
            # Handle delayed email notification
            if not self.env.context.get('delay_email'):
                record._send_notification_email()
        # Handle delayed email notifications using queue job
        if self.env.context.get('delay_email'):
            session = ConnectorSession(self._cr, self._uid)
            _job_send_notification_email.delay(session, self.ids)
        return True

    @api.multi
    def set_in_new_team(self):
        '''
            This method set partner on new team and the date of shifts
        '''
        self.ensure_one()
        current_registrations = self.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.date_begin <= self.new_next_shift_date and (
                not r.date_end or r.date_end >= fields.Date.context_today(self)))
        future_registrations = self.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.date_begin > self.new_next_shift_date and
            r.date_begin >= fields.Date.context_today(self))
        if current_registrations:
            current_registrations[0].date_end = fields.Date.to_string(
                fields.Date.from_string(
                    self.new_next_shift_date) - timedelta(days=1))

        # Add date begin into the first registration template in the future
        # Remove ALL Attendee on this template to create new Attendee on the new team
        # If doesn't have any templates in the future, create a new one

        if future_registrations:
            future_registrations[0].date_begin = self.new_next_shift_date
            for registration in future_registrations:
                registration.shift_registration_ids.unlink()
                registration.shift_template_id = self.new_shift_template_id
        else:
            if self.new_shift_template_id.shift_type_id.is_ftop:
                shift_type = 'ftop'
            else:
                shift_type = 'standard'
            shift_ticket =\
                self.new_shift_template_id.shift_ticket_ids.filtered(
                    lambda t: t.shift_type == shift_type)
            self.env['shift.template.registration.line'].create({
                'shift_template_id': self.new_shift_template_id.id,
                'partner_id': self.partner_id.id,
                'shift_ticket_id': shift_ticket[0].id,
                'date_begin': self.new_next_shift_date,
            })

        # Set days of two next shifts
        date_next_shifts = self.partner_id.registration_ids.filtered(
            lambda r: r.date_begin >=
            fields.Date.context_today(self)).mapped('date_begin')

        self.set_date_future_shifts(date_next_shifts)

        return True

    @api.multi
    def set_date_future_shifts(self, date_next_shifts):
        self.ensure_one()
        range_dates, list_dates = self.compute_range_day()
        if len(date_next_shifts) >= 2:
            self.first_next_shift_date = date_next_shifts[0]
            self.second_next_shift_date = date_next_shifts[1]
        elif len(date_next_shifts) == 1:
            self.first_next_shift_date = date_next_shifts[0]
            if list_dates:
                self.second_next_shift_date = fields.Date.to_string(
                    list_dates[0])
        else:
            if list_dates:
                self.first_next_shift_date = fields.Date.to_string(
                    list_dates[0])
                self.second_next_shift_date = fields.Date.to_string(
                    list_dates[1])

    @api.multi
    @api.depends('new_shift_template_id')
    def compute_full_seats_massagess(self):
        for record in self:
            shift_tmp = record.new_shift_template_id
            if shift_tmp and not shift_tmp.shift_type_id.is_ftop:
                available_standard_seat = 0
                for ticket in shift_tmp.shift_ticket_ids:
                    if ticket.shift_type == 'standard':
                        available_standard_seat += ticket.seats_available
                if available_standard_seat <= 0:
                    record.full_seats_mess = (_(
                        "There is no more seat in this " +
                        " team, would you like to continue?"))
                    record.is_full_seats_mess = True

    @api.multi
    def btn_full_seats_process(self):
        for record in self:
            record.is_full_seats_mess = False
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def convert_state_partner(self):
        self.ensure_one()
        state = self.partner_id.cooperative_state
        if state == 'unsubscribed':
            return (_('Unsubscribed'))
        elif state == 'exempted':
            return (_('Exempted'))
        elif state == 'vacation':
            return (_('Vacation'))
        elif state == 'up_to_date':
            return (_('Up to date'))
        elif state == 'alert':
            return (_('Alert'))
        elif state == 'suspended':
            return (_('Suspended'))
        elif state == 'delay':
            return (_('Delay'))
        elif state == 'blocked':
            return (_('Blocked'))
        elif state == 'unpayed':
            return (_('Unpayed'))
        elif state == 'not_concerned':
            return (_('Not Concerned'))
        else:
            return ''

    @api.multi
    def save_new_without_partner(self):
        self.button_close()
        return {
            'name': _('Change Teams'),
            'type': 'ir.actions.act_window',
            'res_model': 'shift.change.team',
            'view_type': 'form',
            'target': 'new',
            'view_mode': 'form',
            'context': {},
        }

    @api.multi
    def button_save_new(self):
        self.ensure_one()
        partner_ids = self._context.get('partner_ids', [])
        self.button_close()
        changed_team_ids = self._context.get('changed_team_ids', [])

        if not changed_team_ids:
            changed_team_ids = []
        changed_team_ids.append(self.id)

        not_show = self._context.get('not_show_button_next_member', False)
        if not_show:
            return
        if partner_ids:
            partner_id = partner_ids[0]
            partner_ids.remove(partner_ids[0])
            return {
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_partner_id': partner_id,
                            'partner_ids': partner_ids,
                            'changed_team_ids': changed_team_ids},
            }
        elif changed_team_ids:
            return{
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', changed_team_ids)],
                'context': {'not_show_button_next_member': True}
            }
        else:
            return

    @api.multi
    def button_save_close(self):
        self.ensure_one()
        self.button_close()
        changed_team_ids = self._context.get('changed_team_ids', [])
        if not changed_team_ids:
            changed_team_ids = []
        changed_team_ids.append(self.id)

        not_show = self._context.get('not_show_button_next_member', False)
        if not_show:
            return
        if changed_team_ids:
            return{
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', changed_team_ids)],
                'context': {'not_show_button_next_member': True}
            }
        else:
            return

    @api.multi
    def button_next_member(self):
        self.ensure_one()
        partner_ids = self._context.get('partner_ids', [])
        # self.button_close()
        changed_team_ids = self._context.get('changed_team_ids', [])
        if not changed_team_ids:
            changed_team_ids = []
        changed_team_ids.append(self.id)
        if partner_ids:
            partner_id = partner_ids[0]
            partner_ids.remove(partner_ids[0])
            return {
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_partner_id': partner_id,
                            'partner_ids': partner_ids,
                            'changed_team_ids': changed_team_ids, },
            }
        elif changed_team_ids:
            return{
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', changed_team_ids)],
                'context': {'not_show_button_next_member': True}
            }
        else:
            return

    @api.multi
    def convert_format_datatime(self, date_change):
        for record in self:
            if date_change:
                date = date_change.split('-')[2] + '/' +\
                    date_change.split('-')[1] + '/' + date_change.split('-')[0]
                return unicode(date, "utf-8")
            else:
                return unicode('', "utf-8")

    @api.multi
    def compute_current_shift_template(self):
        self.ensure_one()
        if self.partner_id:
            # compute unsubscribed
            if self.partner_id.is_unsubscribed:
                self.partner_state = 'unsubscribed'
                self.show_partner_state = True
                if self.is_catch_up:
                    self.is_catch_up = False
            else:
                self.partner_state = 'subscribed'
                self.show_partner_state = False
            # compute next shift date
            reg = self.partner_id.tmpl_reg_ids.filtered(
                lambda r: r.is_current)
            if reg:
                self.current_shift_template_id = reg[0].shift_template_id
                next_shifts =\
                    self.current_shift_template_id.shift_ids.filtered(
                        lambda s: s.date_begin >= fields.Date.context_today(self))

                self.next_current_shift_date = next_shifts and\
                    next_shifts[0].date_begin or False

    @api.multi
    def check_num_week(self, new_next_shift_date):
        """
        Gets the number of weeks that need to be substracted
        to synchronize with the new shift date
        """
        self.ensure_one()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        n_weeks_cycle = int(get_param('coop_shift.number_of_weeks_per_cycle'))
        week_number = self.env['shift.template']._get_week_number(
            fields.Datetime.from_string(new_next_shift_date).date())
        week_difference = week_number - self.new_shift_template_id.week_number
        return week_difference % n_weeks_cycle

    @api.multi
    def compute_range_day(self):
        '''
        Compute range day base on next shift
            Range day is range of the last shift current team and the date of first shift on new team
        '''
        self.ensure_one()

        next_shifts =\
            self.current_shift_template_id.shift_ids.filtered(
                lambda s: s.date_begin < self.new_next_shift_date).sorted(
                key=lambda l: l.date_begin, reverse=True)

        last_shift_date = next_shifts and next_shifts[0].date_begin or False

        new_team_start_date = fields.Datetime.from_string(
            self.new_next_shift_date).weekday()

        new_next_shift_date = self.new_next_shift_date

        if new_team_start_date > 1 and\
                self.new_shift_template_id.shift_type_id.is_ftop:
            new_next_shift_date = (fields.Datetime.from_string(
                self.new_next_shift_date) - timedelta(
                days=new_team_start_date)).strftime('%Y-%m-%d')

        # This code to handle the rule that use to calculate shifts in the future
        # Making sure the calculation is not miss any shifts
        # I also get shifts in the past and only choose shifts that are greater than
        # the start  date of new shift

        if not self.new_shift_template_id.shift_type_id.is_ftop:
            n_weeks_to_sync = self.check_num_week(new_next_shift_date)
            if n_weeks_to_sync != 0:
                new_next_shift_date = (
                    fields.Datetime.from_string(new_next_shift_date)
                    - timedelta(days=7 * n_weeks_to_sync)
                ).strftime('%Y-%m-%d')

        next_shift_mounth = (
            fields.Datetime.from_string(new_next_shift_date)
            + timedelta(days=90)
        ).strftime('%Y-%m-%d')

        rec_new_template_dates = \
            self.new_shift_template_id.get_recurrent_dates(
                new_next_shift_date, next_shift_mounth)

        for date in rec_new_template_dates:
            if fields.Datetime.to_string(date) < self.new_next_shift_date:
                rec_new_template_dates.remove(date)

        if rec_new_template_dates and last_shift_date:
            date_to_cal = last_shift_date
            if self.new_shift_template_id.shift_type_id.is_ftop:
                date_to_cal = self.new_next_shift_date
            range_dates = rec_new_template_dates[0] -\
                fields.Datetime.from_string(date_to_cal)
            return range_dates.days, rec_new_template_dates
        elif rec_new_template_dates and not last_shift_date:
            if self.new_shift_template_id.shift_type_id.is_ftop:
                range_dates = rec_new_template_dates[0] -\
                    fields.Datetime.from_string(self.new_next_shift_date)
                return range_dates.days, rec_new_template_dates
            else:
                return False, rec_new_template_dates
        else:
            return False, False

    @api.multi
    @api.depends('next_current_shift_date', 'new_shift_template_id',
                 'new_next_shift_date', 'partner_id')
    def compute_mess_change_team(self):
        for record in self:
            if not (record.current_shift_template_id.shift_type_id.is_ftop and
                    not record.new_shift_template_id.shift_type_id.is_ftop):
                record.compute_current_shift_template()
                if record.new_shift_template_id and record.new_next_shift_date:
                    range_dates, list_dates = record.compute_range_day()
                    if not record.current_shift_template_id.shift_type_id.is_ftop\
                            and not record.new_shift_template_id.shift_type_id.is_ftop:
                        if range_dates and range_dates > 40:
                            record.mess_change_team = (_(
                                "Il y a un écart de plus de 6 " +
                                "semaines entre le dernier service dans " +
                                "l’ancienne équipe et le premier avec la nouvelle." +
                                " Souhaitez-vous continuer ?"))
                            record.is_abcd_to_abcd = True
                            record.is_mess_change_team = True
                    elif record.new_shift_template_id.shift_type_id.is_ftop:
                        if range_dates <= 14:
                            record.mess_change_team = (_(
                                "La date de démarrage est inférieure à 15 jours " +
                                " avant le jour de décompte volant qui suit. " +
                                "Souhaitez-vous continuer ?"
                            ))
                            record.is_mess_change_team = True

    @api.multi
    def btn_change_team_process(self):
        for record in self:
            record.is_mess_change_team = False
        return {
            "type": "ir.actions.do_nothing",
        }


@job
def _job_send_notification_email(session, rec_ids):
    session.env['shift.change.team'].browse(rec_ids)._send_notification_email()
