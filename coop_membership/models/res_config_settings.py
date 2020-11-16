from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    description = fields.Html()
    notice = fields.Html()
    email_meeting_contact = fields.Char(
        related='company_id.email_meeting_contact',
        readonly=False,
    )
    company_name = fields.Char(
        related='company_id.company_name',
        readonly=False,
    )
    max_nb_associated_people = fields.Integer(
        'Maximum Associated People',
        config_parameter="coop_membership.max_nb_associated_people",
    )
    associated_people_available = fields.Selection([
        ('unlimited', 'Unlimited'),
        ('limited', 'Limited')
        ],
        config_parameter='coop_membership.associated_people_available',
        default='unlimited',
    )
    contact_us_messages = fields.Html(
        string="Contact Us Message",
        related="company_id.contact_us_message",
        translate=True,
        readonly=False,
    )
    max_registrations_per_day = fields.Integer(
        string='FTOP Max. Registration per day',
        related="company_id.max_registrations_per_day",
        readonly=False,
    )
    max_registration_per_period = fields.Integer(
        string='FTOP Max. Registration per period',
        related="company_id.max_registration_per_period",
        readonly=False,
    )
    number_of_days_in_period = fields.Integer(
        string='FTOP Registration period',
        related="company_id.number_of_days_in_period",
        readonly=False,
    )
    maximum_active_days = fields.Integer(
        related="company_id.maximum_active_days",
        readonly=False,
    )
    members_office_open_hours = fields.Text(
        related='company_id.members_office_open_hours',
        string="Members Office Open Hours",
        translate=True,
        readonly=False,
    )

    @api.multi
    @api.constrains('number_of_days_in_period')
    def _check_positive_number_of_days_in_period(self):
        for config in self:
            if config.number_of_days_in_period < 0:
                raise ValidationError(_(
                    "The FTOP Max. Registration per period "
                    "number must be a positive number !"))

    @api.multi
    @api.constrains('max_nb_associated_people')
    def _check_positive_number_of_associated_people(self):
        for rec in self:
            if rec.max_nb_associated_people < 0:
                raise ValidationError(_(
                    "The maximum number of associated people must be a "
                    "positive number !"))

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        description = self.env["ir.config_parameter"].sudo().get_param(
            "account_export.notice", default=None)
        notice = self.env["ir.config_parameter"].sudo().get_param(
            "account_export.notice", default=None)
        res.update(description=description or False)
        res.update(notice=notice or False)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "account_export.description", self.description or '')
        self.env['ir.config_parameter'].sudo().set_param(
            "account_export.notice", self.notice or '')
