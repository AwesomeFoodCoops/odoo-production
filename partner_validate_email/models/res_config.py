# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    validate_email = fields.Boolean(
        "Enable verification of domain when" +
        " checking an email address",
        default=False,
        config_parameter='partner_validate_email.validate_email')
