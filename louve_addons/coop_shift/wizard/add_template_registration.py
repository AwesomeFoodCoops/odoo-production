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
from datetime import datetime

STATES = [
    ('cancel', 'Cancelled'),
    ('draft', 'Unconfirmed'),
    ('open', 'Confirmed'),
    ('done', 'Attended'),
    ('absent', 'Absent'),
    ('waiting', 'Waiting'),
    ('excused', 'Excused'),
    ('replaced', 'Replaced'),
    ('replacing', 'Replacing'),
]


class AddTemplateRegistration(models.TransientModel):
    _name = 'add.template.registration.wizard'
    _description = 'Add Template Registration Wizard'

    template_id = fields.Many2one('shift.template', "Template", required=True)
    shift_ticket_id = fields.Many2one(
        'shift.template.ticket', "Ticket", required=True)
    date_begin = fields.Date(
        "Begin Date", default=lambda *a: datetime.now().strftime('%Y-%m-%d'))
    date_end = fields.Date("End Date")
    state = fields.Selection(STATES, "State", default="open")

    @api.multi
    def add_template_registration(self):
        partner = self.env['res.partner'].browse(
            self.env.context.get('active_id', False))
        if not partner:
            return False

        for wizard in self:
            values = {
                'line_ids': [(0, 0, {
                    'date_begin': wizard.date_begin,
                    'date_end': wizard.date_end,
                    'state': wizard.state,
                })]
            }
            registration = wizard.shift_ticket_id.registration_ids.filtered(
                lambda r, p=partner: r.partner_id == p)
            if registration:
                registration.write(values)
            else:
                values = dict(values, **{
                    'shift_template_id': wizard.template_id.id,
                    'partner_id': partner.id,
                    'shift_ticket_id': wizard.shift_ticket_id.id,
                })
                self.env['shift.template.registration'].create(values)

    @api.onchange('template_id')
    def onchange_template_id(self):
        self.shift_ticket_id = False
