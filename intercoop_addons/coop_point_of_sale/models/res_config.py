# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from openerp.tools.safe_eval import safe_eval


class PosConfiguration(models.TransientModel):
    _inherit = 'pos.config.settings'

    diacritics_insensitive_search = fields.Boolean(
        default=False,
        string="Make products searchs insensitive to diacritics "
        "(ignore accents)")

    @api.multi
    def set_params(self):
        self.ensure_one()
        ir_config_env = self.env['ir.config_parameter']
        value = getattr(self, 'diacritics_insensitive_search', False)
        ir_config_env.set_param('diacritics_insensitive_search', repr(value))

    @api.multi
    def get_default_params(self):
        res = {}
        ir_config_env = self.env['ir.config_parameter']
        res['diacritics_insensitive_search'] = safe_eval(
            ir_config_env.get_param('diacritics_insensitive_search', 'False'))
        return res
