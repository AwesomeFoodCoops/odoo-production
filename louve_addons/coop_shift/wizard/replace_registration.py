# -*- encoding: utf-8 -*-
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


class ReplaceRegistration(models.TransientModel):
    _name = 'replace.registration.wizard'
    _description = 'Replace Registration Wizard'

    @api.model
    def _get_registration_id(self):
        return self.env.context.get('active_id', False)

    registration_id = fields.Many2one(
        'shift.registration', "Registration", default=_get_registration_id,
        required=True, ondelete="cascade")
    shift_id = fields.Many2one(
        related='registration_id.shift_id',
        readonly=True)
    shift_ticket_id = fields.Many2one(
        string="Shift Ticket", related='registration_id.shift_ticket_id',
        readonly=True)
    date_begin = fields.Datetime(related="shift_id.date_begin", readonly=True)
    date_end = fields.Datetime(related="shift_id.date_end", readonly=True)
    partner_id = fields.Many2one(
        string="Replaced Member", related='registration_id.partner_id',
        readonly=True)
    new_partner_id = fields.Many2one(
        'res.partner', "Replacing Member", required=True)
    email = fields.Char(readonly=True, related='new_partner_id.email')
    phone = fields.Char(readonly=True, related='new_partner_id.phone')
    name = fields.Char(readonly=True, related='new_partner_id.name')

    @api.multi
    def replace_member(self):
        for wizard in self:
            new_reg_id = wizard.registration_id.copy({
                'partner_id': wizard.new_partner_id.id,
                'state': 'replacing',
                'replaced_reg_id': wizard.registration_id.id,
                'tmpl_reg_line_id': False, }, )
            wizard.registration_id.state = "replaced"
            wizard.registration_id.replacing_reg_id = new_reg_id.id
            shift_id = wizard.registration_id.shift_id
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'shift.registration',
            'context': {'search_default_shift_id': shift_id.id},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
