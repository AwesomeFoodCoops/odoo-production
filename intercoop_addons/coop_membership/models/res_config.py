# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


PARAMS = [
    ("max_nb_associated_people", "coop_membership.max_nb_associated_people"),
    ("associated_people_available",
     "coop_membership.associated_people_available"),
]


class MembersConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'members.config.settings'

    max_nb_associated_people = fields.Integer('Maximum Associated People')
    associated_people_available = fields.Selection([
        ('unlimited', 'Unlimited'),
        ('limited', 'Limited')], default='unlimited')
    contact_us_messages = fields.Html(
        string="Contact Us Message", translate=True)

    max_registrations_per_day = fields.Integer(
        string='FTOP Max. Registration per day'
    )
    max_registration_per_period = fields.Integer(
        string='FTOP Max. Registration per period'
    )
    number_of_days_in_period = fields.Integer(
        string='FTOP Registration period'
    )

    maximum_active_days = fields.Integer()

    @api.multi
    @api.constrains('number_of_days_in_period')
    def _check_positive_number_of_days_in_period(self):
        for config in self:
            if config.number_of_days_in_period < 0:
                raise ValidationError(
                    _("The FTOP Max. Registration per period number must be a positive number !")
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
                raise ValidationError(_("The maximum number of " +
                                        "associated people must be a positive number !"))

    @api.multi
    def set_params(self):
        self.ensure_one()
        for field_name, key_name in PARAMS:
            value = getattr(self, field_name, False)
            self.env['ir.config_parameter'].set_param(key_name, value)

    @api.multi
    def get_default_params(self):
        config_param_env = self.env['ir.config_parameter']
        key_max_nb = 'coop_membership.max_nb_associated_people'
        max_nb = eval(config_param_env.get_param(key_max_nb, '0'))
        key_avail_check = 'coop_membership.associated_people_available'
        avail_check = config_param_env.get_param(key_avail_check, 'unlimited')
        return {'max_nb_associated_people': max_nb,
                'associated_people_available': avail_check
                }

    @api.model
    def default_get(self, fields):
        res = super(MembersConfiguration, self).default_get(fields)
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

        return super(MembersConfiguration, self).execute()
