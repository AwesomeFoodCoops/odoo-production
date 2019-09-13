# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class CapitalFundraisingPartnerType(models.Model):
    _name = 'capital.fundraising.partner.type'
    _description = 'Capital Fundraising Partner Type'

    name = fields.Char(string='Name', required=True)
