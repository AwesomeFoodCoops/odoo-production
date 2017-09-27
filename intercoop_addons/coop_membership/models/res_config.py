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

