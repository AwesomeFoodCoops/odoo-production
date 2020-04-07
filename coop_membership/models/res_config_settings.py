from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    seats_max = fields.Integer(string='Maximum Attendees Number')
    description = fields.Html(string='Description', translate=False)
    notice = fields.Html("Notice")
    email_meeting_contact = fields.Char(
        related='company_id.email_meeting_contact',
        readonly=False,
    )
    company_name = fields.Char(
        related='company_id.company_name',
        readonly=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # seats_max = self.env["ir.config_parameter"].get_param(
        #     "account_export.seats_max")
        description = self.env["ir.config_parameter"].get_param(
            "account_export.description", default=None)
        notice = self.env["ir.config_parameter"].get_param(
            "account_export.notice", default=None)
        # res.update(seats_max=seats_max or False)
        res.update(description=description or False)
        res.update(notice=notice or False)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # self.env['ir.config_parameter'].set_param(
        #     "account_export.seats_max", self.seats_max)
        self.env['ir.config_parameter'].set_param(
            "account_export.description", self.description or '')
        self.env['ir.config_parameter'].set_param(
            "account_export.notice", self.notice or '')

    @api.multi
    def execute(self):
        has_group_event_manager = \
            self.env.user.has_group('event.group_event_manager')
        if has_group_event_manager:
            return super(ResConfigSettings, self.sudo()).execute()
        return super(ResConfigSettings, self).execute()
