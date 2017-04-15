# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    capital_certificate_header = fields.Char(
        "Capital Certificate Header",
        related='company_id.capital_certificate_header',
        help="example: 'La S.A.S. Coopérative à Capital Variable LA LOUVE'")
    capital_account_ids = fields.One2many(
        string='Capital Partner Accounts', comodel_name='account.account',
        inverse_name='capital_certificate_config_id',
        related='company_id.capital_account_ids',
        help="""List here all Capital concerned Partner Accounts. They will"""
        """ be used to know if a partner paid his subscription.""")
