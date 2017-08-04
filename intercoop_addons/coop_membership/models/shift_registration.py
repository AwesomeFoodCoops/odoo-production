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

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id', False)
        partner = self.env['res.partner'].browse(partner_id)
        if partner.is_unsubscribed and not self.env.context.get(
                'creation_in_progress', False):
            raise UserError(_(
                """You can't register this partner on a shift because """
                """he isn't registered on a template"""))
        return super(ShiftRegistration, self).create(vals)

    @api.multi
    def action_create_extension(self):
        '''
        @Function triggered by a button on Attendance tree view
        to create extension automatically for a member:
            - Extension Type: Extension
            - Start Date: registration start date
            - End Date: Next Shift Date
        '''
        shift_extension_env = self.env['shift.extension']
        for registration in self:
            partner = registration.partner_id
            extension_type = self.env.ref(
                'coop_membership.shift_extension_type_extension')

            date_begin_obj = datetime.strptime(
                registration.date_begin, '%Y-%m-%d %H:%M:%S')
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
