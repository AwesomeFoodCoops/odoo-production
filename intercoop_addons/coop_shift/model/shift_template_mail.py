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

from openerp import models, fields


class ShiftTemplateMailScheduler(models.Model):
    """ Shift automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on shifts since Odoo 9. A cron exists
    that periodically checks for mailing to run. """
    _name = 'shift.template.mail'

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
