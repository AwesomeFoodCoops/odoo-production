# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

PARAMS = [
    ("max_nb_associated_people", "coop_membership.max_nb_associated_people"),
    ("associated_people_available",
     "coop_membership.associated_people_available"),
]


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    max_nb_associated_people = fields.Integer('Maximum Associated People')
    associated_people_available = fields.Selection(
        [('unlimited', 'Unlimited'),
         ('limited', 'Limited')], default='unlimited')
    contact_us_messages = fields.Html(
        related="company_id.contact_us_message",
        string="Contact Us Message", translate=True, readonly=False)
    max_registrations_per_day = fields.Integer(
        related="company_id.max_registrations_per_day",
        string='FTOP Max. Registration per day', readonly=False)
    max_registration_per_period = fields.Integer(
        related="company_id.max_registration_per_period",
        string='FTOP Max. Registration per period', readonly=False)
    number_of_days_in_period = fields.Integer(
        related="company_id.number_of_days_in_period",
        string='FTOP Registration period', readonly=False)
    maximum_active_days = fields.Integer(
        related="company_id.maximum_active_days", readonly=False)
    members_office_open_hours = fields.Text(
        related='company_id.members_office_open_hours',
        string="Members Office Open Hours", translate=True, readonly=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_obj = self.env["ir.config_parameter"]
        max_nb_associated_people = config_obj.sudo().get_param(
            "coop_membership.max_nb_associated_people", default=0)
        associated_people_available = config_obj.get_param(
            "coop_membership.associated_people_available")

        res.update(max_nb_associated_people=int(max_nb_associated_people))
        res.update(associated_people_available=associated_people_available)
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_obj = self.env["ir.config_parameter"]
        config_obj.sudo().set_param(
            "coop_membership.max_nb_associated_people",
            self.max_nb_associated_people
        )
        config_obj.set_param(
            "coop_membership.associated_people_available",
            self.associated_people_available)
        config_obj.set_param(
            "coop_membership.contact_us_messages", self.contact_us_messages)

    @api.multi
    @api.constrains('number_of_days_in_period')
    def _check_positive_number_of_days_in_period(self):
        for config in self:
            if config.number_of_days_in_period < 0:
                raise ValidationError(
                    _("The FTOP Max. Registration per period"
                      "number must be a positive number !")
                )

    @api.multi
    @api.constrains('max_nb_associated_people')
    def _check_positive_number_of_associated_people(self):
        '''
        @Function to add a constraint on field maximum number of associated
            people
            - Input number is positive number
        '''
        for rc in self:
            if rc.max_nb_associated_people < 0:
                raise ValidationError(_("""
                The maximum number of
                associated people must be a positive number !
                """))
