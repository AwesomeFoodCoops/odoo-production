# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    email_pos_receipt = fields.Boolean(
        string="E-receipt",
        default=False,
        help="If you tick this box and option 3 is selected for 'Receipt' in point of sale settings, the user will only receive e-receipt")
