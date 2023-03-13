# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ShiftMailRegistration(models.Model):
    _inherit = 'event.mail.registration'
    _name = 'shift.mail.registration'

    scheduler_id = fields.Many2one(
        'shift.mail', 'Mail Scheduler', required=True, ondelete='cascade')
    registration_id = fields.Many2one(
        'shift.registration', 'Attendee', required=True, ondelete='cascade')
    mail_ignored = fields.Boolean('Ignored', default=False)
    scheduled_date = fields.Datetime(
        'Scheduled Time', related="scheduler_id.scheduled_date", store=True)

    @api.multi
    def execute(self):
        today = fields.datetime.now()
        records_to_execute = self.filtered(
            lambda rec: rec.registration_id.shift_id.date_begin >= today)
        records_to_ignore = self - records_to_execute
        records_to_skip = records_to_execute.filtered(
            lambda rec: rec.registration_id.partner_id.working_state
            in ['exempted', 'vacation'])
        records_to_execute -= records_to_skip
        if records_to_ignore:
            records_to_ignore.write({'mail_ignored': True})
        return super(ShiftMailRegistration, records_to_execute).execute()
