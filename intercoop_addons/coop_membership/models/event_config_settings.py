# -*- coding: utf-8 -*-

from openerp import api, models, fields


class EventConfigSettings(models.Model):
    _inherit = 'event.config.settings'

    seats_max = fields.Integer(gitstring='Maximum Attendees Number')
    description = fields.Html(string='Description', translate=False)
    notice = fields.Html("Notice")

    @api.model
    def get_default_seats_max(self, fields):
        seats_max = self.env['ir.values'].get_default(
            'event.config.settings', 'seats_max')
        return {
            'seats_max': seats_max,
        }

    @api.multi
    def set_default_seats_max(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'event.config.settings', 'seats_max',
            self.seats_max or 0)

    @api.model
    def get_default_description(self, fields):
        description = self.env['ir.values'].get_default(
            'event.config.settings', 'description')
        return {
            'description': description,
        }

    @api.multi
    def set_default_description(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'event.config.settings', 'description',
            self.description or "")

    @api.model
    def get_default_notice(self, fields):
        notice = self.env['ir.values'].get_default(
            'event.config.settings', 'notice')
        return {
            'notice': notice,
        }

    @api.multi
    def set_default_notice(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'event.config.settings', 'notice',
            self.notice or "")
