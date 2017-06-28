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


class ShiftRegistration(models.Model):
    _inherit = 'shift.registration'

    partner_id = fields.Many2one(
        domain=[('is_worker_member', '=', True)])

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
