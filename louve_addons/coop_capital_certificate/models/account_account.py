# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    capital_certificate_config_id = fields.Many2one(
        comodel_name="capital.certificate.config")
