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

from openerp import models, fields, api, _


class ShiftTemplate(models.Model):
    _inherit = 'shift.template'

    user_ids = fields.Many2many(
        domain=[('is_worker_member', '=', True)])

    warning_leader_unsubscribed = fields.Html(
        compute="_compute_warning_leader_unsubscribed",
        string="Warning unsubscribed leader",
        store=True,
    )
    registration_qty = fields.Integer(
        string='Number of Attendees', compute='_compute_registration_qty',
        store=True
    )

    @api.multi
    @api.depends('registration_ids')
    def _compute_registration_qty(self):
        for template in self:
            current_regs = template.registration_ids.filtered(
                lambda reg: reg.is_current_participant
            )
            template.registration_qty = len(current_regs)

    @api.multi
    @api.depends('user_ids', 'user_ids.is_unsubscribed')
    def _compute_warning_leader_unsubscribed(self):
        for template in self:
            if len(template.user_ids) == 1 and\
                    template.user_ids[0].is_unsubscribed:
                template.warning_leader_unsubscribed = (_(
                    "Please choose another leader because" +
                    " the current leader is unsubscribed"))
            else:
                template.warning_leader_unsubscribed = False
