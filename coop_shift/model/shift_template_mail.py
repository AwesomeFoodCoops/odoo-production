# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ShiftTemplateMailScheduler(models.Model):
    """ Shift automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on shifts since Odoo 9. A cron exists
    that periodically checks for mailing to run. """
    _name = 'shift.template.mail'
    _description = 'Shift Template Mail'

    shift_template_id = fields.Many2one(
        'shift.template', string='Shift Template',
        required=True, ondelete='cascade')
    sequence = fields.Integer('Display order')
    interval_nbr = fields.Integer('Interval', default=1)
    interval_unit = fields.Selection([
        ('now', 'Immediately'),
        ('hours', 'Hour(s)'), ('days', 'Day(s)'),
        ('weeks', 'Week(s)'), ('months', 'Month(s)')],
        string='Unit', default='hours', required=True)
    interval_type = fields.Selection([
        ('after_sub', 'After each subscription'),
        ('before_shift', 'Before the shift'),
        ('after_shift', 'After the shift')],
        string='When to Run ', default="before_shift", required=True)
    template_id = fields.Many2one(
        'mail.template', string='Email to Send', ondelete='restrict',
        domain=[('model', '=', 'shift.registration')], required=True,
        help="""This field contains the template of the mail that will be
        automatically sent""")
