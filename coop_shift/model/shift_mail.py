# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

_INTERVALS = {
    'hours': lambda interval: relativedelta(hours=interval),
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
    'now': lambda interval: relativedelta(hours=0),
}


class ShiftMailScheduler(models.Model):
    """ Shift automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on events since Odoo 9. A cron exists
    that periodically checks for mailing to run. """
    _inherit = 'event.mail'
    _name = 'shift.mail'

    event_id = fields.Many2one(required=False)
    shift_id = fields.Many2one(
        'shift.shift', string='Shift', required=True, ondelete='cascade')
    mail_registration_ids = fields.One2many(
        'shift.mail.registration', 'scheduler_id')
    template_id = fields.Many2one(
        'mail.template', string='Email to Send', ondelete='restrict',
        domain=[('model', '=', 'shift.registration')], required=True,
        help="""This field contains the template of the mail that will be
        automatically sent""")

    @api.multi
    @api.depends(
        'mail_sent', 'interval_type', 'shift_id.registration_ids',
        'mail_registration_ids')
    def _compute_done(self):
        for rec in self:
            if rec.interval_type in ['before_event', 'after_event']:
                rec.done = rec.mail_sent
            else:
                rec.done = len(
                    rec.mail_registration_ids) == len(
                    rec.shift_id.registration_ids) and all(
                    filter(
                        lambda line: line.mail_sent,
                        rec.mail_registration_ids))

    @api.multi
    @api.depends(
        'shift_id.state',
        'shift_id.date_begin',
        'interval_type',
        'interval_unit',
        'interval_nbr')
    def _compute_scheduled_date(self):
        for rec in self:
            if rec.shift_id.state not in ['confirm', 'done']:
                rec.scheduled_date = False
            else:
                if rec.interval_type == 'after_sub':
                    date, sign = rec.shift_id.create_date, 1
                elif rec.interval_type == 'before_event':
                    date, sign = rec.shift_id.date_begin, -1
                else:
                    date, sign = rec.shift_id.date_end, 1
                rec.scheduled_date = (
                    date
                    + _INTERVALS[rec.interval_unit](sign * rec.interval_nbr)
                )

    @api.multi
    def execute(self):
        for sm in self:
            if sm.shift_id.shift_type_id.is_ftop:
                continue
            if sm.shift_id.state != 'confirm':
                continue
            if sm.interval_type in ['after_sub', 'before_event']:
                # update registration lines
                lines = []
                for registration in filter(lambda item: item not in [
                        mail_reg.registration_id for mail_reg in
                        sm.mail_registration_ids],
                        sm.shift_id.registration_ids):
                    lines.append((0, 0, {'registration_id': registration.id}))
                if lines:
                    sm.write({'mail_registration_ids': lines})
                # execute scheduler on registrations
                today = fields.Datetime.now()
                # filter mails with ignoring conditions.
                sm.mail_registration_ids.filtered(
                    lambda reg: reg.scheduled_date and
                    reg.scheduled_date <= today and
                    not reg.mail_ignored
                ).sudo().execute()
            else:
                if not sm.mail_sent:
                    sm.shift_id.mail_attendees(sm.template_id.id)
                    sm.write({'mail_sent': True})
            return True

    @api.model
    def run(self, autocommit=False):
        today = fields.Datetime.to_string(fields.Datetime.now())
        schedulers = self.search([
            ('done', '=', False),
            ('scheduled_date', '<=', today),
        ])
        for scheduler in schedulers:
            try:
                with self.env.cr.savepoint():
                    scheduler.execute()
            except Exception as e:
                _logger.exception(e)
                self.invalidate_cache()
                self._warn_template_error(scheduler, e)
        return True

    def update_interval_type(self, vals):
        if vals.get("interval_type"):
            # Replace the value something likes "before_shift", "after_shift"
            # by "before_event", "after_event"
            vals["interval_type"] = vals["interval_type"].replace("shift", "event")
        return vals

    @api.model
    def create(self, vals):
        self.update_interval_type(vals)
        res = super(ShiftMailScheduler, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        self.update_interval_type(vals)
        return super(ShiftMailScheduler, self).write(vals)
