# -*- coding: utf-8 -*-

from openerp import api, models, fields

PARAMS = [
    ("description", "coop_membership.description_event_config_settings"),
    ("notice", "coop_membership.notice_event_config_settings"),
]

class EventConfigSettings(models.TransientModel):
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

    @api.multi
    def get_default_params(self):
        config_param_env = self.env['ir.config_parameter']
        return {
            field_name: config_param_env.get_param(parameter_key, '')
            for field_name, parameter_key in PARAMS
        }

    @api.multi
    def set_params(self):
        self.ensure_one()
        config_param_env = self.env['ir.config_parameter']
        for field_name, key_name in PARAMS:
            value = getattr(self, field_name, False)
            config_param_env.set_param(key_name, value)

    @api.multi
    def execute(self):
        has_group_event_manager = \
            self.env.user.has_group('event.group_event_manager')
        if has_group_event_manager:
            return super(EventConfigSettings, self.sudo()).execute()
        return super(EventConfigSettings, self).execute()

