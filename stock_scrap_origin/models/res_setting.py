# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    scrap_origin_required = fields.Boolean(
        config_parameter='scrap_order.scrap_origin_required',
    )
