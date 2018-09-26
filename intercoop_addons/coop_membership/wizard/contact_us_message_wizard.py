# -*- coding: utf-8 -*-

from openerp import api, models, fields


class ContactUsMessageWizard(models.TransientModel):
    _name = 'contact.us.message.wizard'

    message = fields.Text(
        string="Contact Us Message")
    partner_id = fields.Many2one(
        'res.partner', string="Member", required=1)

    @api.multi
    def button_ok(self):
        self.ensure_one()
        self.partner_id.contact_us_message = self.message
        return True
