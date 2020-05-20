# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models


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
    email_meeting_contact = fields.Char()
    company_name = fields.Char()
    office_timing = fields.Text(
        string='Office Timing',
        translate=True,
        default=lambda self: self.get_default_timing())

    @api.model
    def get_default_message(self):
        return u"""Hello,<br/>Please contact an employee or go at the members\'
        office for administrative reasons.<br/>
        Cordially, {} team""".format(self.env.user.company_id.name)

    @api.model
    def get_default_timing(self):
        return u"""Tuesday: 1:30 p.m. - 4 p.m. \n
        Wednesday to Friday: 1:30 p.m. - 8 p.m.
        \n Saturday: 10 a.m. - 4 p.m."""
