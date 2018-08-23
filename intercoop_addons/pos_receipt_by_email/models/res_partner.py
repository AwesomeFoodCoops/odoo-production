# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    email_pos_receipt = fields.Boolean(
        string="Send email POS",
        default=False)
