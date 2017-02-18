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

    registration_ids = fields.One2many(
        'shift.registration', "partner_id", 'Registrations')
    upcoming_registration_count = fields.Integer(
        "Number of registrations", compute="_compute_registration_counts")
    next_registration_id = fields.One2many(
        'shift.registration', "partner_id", 'Next Registration',
        compute="_compute_registration_counts")

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

    current_tmpl_reg_line_ids = fields.One2many(
        'shift.template.registration.line', "partner_id",
        'Current Template')

    current_template_name = fields.Char(
        string='Current Template', compute='_compute_current_template_name')

    is_squadleader = fields.Boolean(
        "is an active Squadleader", compute="_compute_is_squadleader")
    template_ids = fields.Many2many(
        'shift.template', 'res_partner_shift_template_rel',
        'partner_id', 'shift_template_id', string='Leader on these templates')

    # Compute section
    @api.multi
    def _compute_registration_counts(self):
        d = fields.Datetime.now()
        for partner in self:
            next_registrations = partner.registration_ids.filtered(
                lambda r, d=d: r.date_begin >= d)
            partner.upcoming_registration_count = len(next_registrations)
            next_registrations = next_registrations.sorted(
                lambda r: r.date_begin)
            partner.next_registration_id = next_registrations and\
                next_registrations[0] or False
            partner.tmpl_registration_count = len(partner.tmpl_reg_line_ids)
            partner.active_tmpl_reg_line_count = len(
                partner.tmpl_reg_line_ids.filtered(
                    lambda l: l.is_current or l.is_future))
            partner.current_tmpl_reg_line_ids =\
                partner.tmpl_reg_line_ids.filtered(lambda l: l.is_current)

    @api.multi
    def _compute_current_template_name(self):
        for partner in self:
            reg = partner.tmpl_reg_ids.filtered(
                lambda r: r.is_current)
            if reg:
                partner.current_template_name = reg[0].shift_template_id.name
            else:
                reg = partner.tmpl_reg_ids.filtered(
                    lambda r: r.is_future)
                if reg:
                    partner.current_template_name =\
                        reg[0].shift_template_id.name

    # Compute section
    @api.multi
    def _compute_is_squadleader(self):
        for partner in self:
            partner.is_squadleader = False
            shifts = self.env['shift.shift'].search([
                ('user_ids', 'in', partner.id),
                ('date_begin', '>=', fields.Date.today())
            ])
            if len(shifts):
                partner.is_squadleader = True
