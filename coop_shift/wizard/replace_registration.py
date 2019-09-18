# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


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
                'replaced_reg_id': wizard.registration_id.id,
                'tmpl_reg_line_id': False,
                'template_created': False,
                'state': 'replacing'})
            wizard.registration_id.state = "replaced"
            wizard.registration_id.replacing_reg_id = new_reg_id.id
        return True
