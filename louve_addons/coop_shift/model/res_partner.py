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

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_registration_counts(self):
        d = fields.Datetime.now()
        for partner in self:
            partner.upcoming_registration_count = len(
                partner.registration_ids.filtered(
                    lambda r, d=d: r.date_begin >= d))
            partner.tmpl_registration_count = len(partner.tmpl_reg_line_ids)
            partner.active_tmpl_reg_line_count = len(
                partner.tmpl_reg_line_ids.filtered(
                    lambda l: l.is_current is True))

    registration_ids = fields.One2many(
        'shift.registration', "partner_id", 'Registrations')
    upcoming_registration_count = fields.Integer(
        "Number of registrations", compute="_compute_registration_counts")
    tmpl_reg_ids = fields.One2many(
        'shift.template.registration', "partner_id",
        'Template Registrations')
    tmpl_reg_line_ids = fields.One2many(
        'shift.template.registration.line', "partner_id",
        'Template Registration Lines')
    tmpl_registration_count = fields.Integer(
        "Number of Template registrations",
        compute="_compute_registration_counts")
    active_tmpl_reg_line_count = fields.Integer(
        "Number of active registration lines",
        compute="_compute_registration_counts")
