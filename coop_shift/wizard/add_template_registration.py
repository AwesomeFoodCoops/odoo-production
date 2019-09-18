# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from ..model.date_tools import conflict_period

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
        "Begin Date", default=lambda *a: fields.Date.today())
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
                registration = \
                    self.env['shift.template.registration'].create(values)

        # Reupdate the leave on the registration updated or created.
        # Search for approved leaves within the period
        reg_line_ids = []
        for reg in registration:
            reg_line_ids += reg.line_ids.ids

        approved_leaves = self.env['shift.leave'].search(
            [('partner_id', '=', partner.id),
             ('state', '=', 'done')])
        for leave in approved_leaves:
            if conflict_period(leave.start_date, leave.stop_date,
                               wizard.date_begin, wizard.date_end,
                               True)['conflict']:
                # Apply the leave to the registrations
                leave_wizard = self.env['shift.leave.wizard'].create({
                    'leave_id': leave.id,
                    'shift_template_registration_line_ids':
                    [(4, reg_id) for reg_id in reg_line_ids]
                })
                leave_wizard.with_context(
                    bypass_non_draft_confirm=True).button_confirm()

    @api.onchange('template_id')
    def onchange_template_id(self):
        self.shift_ticket_id = False
