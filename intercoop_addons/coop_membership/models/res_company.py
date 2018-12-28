# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    contact_us_message = fields.Html(
        string="Contact Us Message",
        translate=True,
        default=lambda self: self.get_default_message()
    )
    max_registrations_per_day = fields.Integer(default=2)
    max_registration_per_period = fields.Integer(default=5)
    number_of_days_in_period = fields.Integer(default=28)

    maximum_active_days = fields.Integer(default=180)

    @api.model
    def get_default_message(self):
        return u"Bonjour,<br/>Veuillez contacter un salarié ou vous rendre au bureau des membres pour une raison administrative.<br/>Cordialement, L'équipe {}".format(self.env.user.company_id.name)
