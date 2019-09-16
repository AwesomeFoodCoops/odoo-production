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
    contact_us_messages = fields.Html(string="Contact Us Message",
                                      translate=True)
    max_registrations_per_day = fields.Integer(
        string='FTOP Max. Registration per day')
    max_registration_per_period = fields.Integer(
        string='FTOP Max. Registration per period')
    number_of_days_in_period = fields.Integer(
        string='FTOP Registration period')
    maximum_active_days = fields.Integer()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_obj = self.env["ir.config_parameter"]
        max_nb_associated_people = config_obj.get_param(
            "coop_membership.max_nb_associated_people", default=0)
        associated_people_available = config_obj.get_param(
            "coop_membership.associated_people_available")
        contact_us_messages = config_obj.get_param(
            "coop_membership.contact_us_messages")
        max_registrations_per_day = config_obj.get_param(
            "coop_membership.max_registrations_per_day", default=0)
        max_registration_per_period = config_obj.get_param(
            "coop_membership.max_registration_per_period", default=0)
        number_of_days_in_period = config_obj.get_param(
            "coop_membership.number_of_days_in_period", default=0)
        maximum_active_days = config_obj.get_param(
            "coop_membership.maximum_active_days", default=0)

        res.update(max_nb_associated_people=int(max_nb_associated_people))
        res.update(associated_people_available=associated_people_available)
        res.update(contact_us_messages=contact_us_messages)
        res.update(max_registrations_per_day=int(max_registrations_per_day))
        res.update(
            max_registration_per_period=int(max_registration_per_period))
        res.update(number_of_days_in_period=int(number_of_days_in_period))
        res.update(maximum_active_days=int(maximum_active_days))
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_obj = self.env["ir.config_parameter"]
        config_obj.set_param("coop_membership.max_nb_associated_people",
                             self.max_nb_associated_people)
        config_obj.set_param(
            "coop_membership.associated_people_available",
            self.associated_people_available)
        config_obj.set_param(
            "coop_membership.contact_us_messages", self.contact_us_messages)
        config_obj.set_param("coop_membership.max_registrations_per_day",
                             self.max_registrations_per_day)
        config_obj.set_param("coop_membership.max_registration_per_period",
                             self.max_registration_per_period)
        config_obj.set_param("coop_membership.number_of_days_in_period",
                             self.number_of_days_in_period)
        config_obj.set_param("coop_membership.maximum_active_days",
                             self.maximum_active_days)

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

    @api.model
    def default_get(self, fields):
        res = super(ResConfigSettings, self).default_get(fields)
        company = self.env.user.company_id
        message = company.contact_us_message
        max_registrations_per_day = company.max_registrations_per_day
        max_registration_per_period = company.max_registration_per_period
        number_of_days_in_period = company.number_of_days_in_period
        maximum_active_days = company.maximum_active_days

        if 'contact_us_messages' in fields:
            res.update({
                'contact_us_messages': message,
                'max_registrations_per_day': max_registrations_per_day,
                'max_registration_per_period': max_registration_per_period,
                'number_of_days_in_period': number_of_days_in_period,
                'maximum_active_days': maximum_active_days,
            })
        return res

    @api.multi
    def execute(self):
        company = self.env.user.company_id
        for record in self:
            company.contact_us_message = record.contact_us_messages
            company.max_registrations_per_day = \
                record.max_registrations_per_day
            company.max_registration_per_period = \
                record.max_registration_per_period
            company.number_of_days_in_period = \
                record.number_of_days_in_period

            company.maximum_active_days = record.maximum_active_days

        return super(ResConfigSettings, self).execute()
