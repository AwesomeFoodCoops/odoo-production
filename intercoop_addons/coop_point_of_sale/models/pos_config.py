# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from openerp.tools.safe_eval import safe_eval


class PosConfig(models.Model):
    _inherit = 'pos.config'

    diacritics_insensitive_search = fields.Boolean(
        default=False,
        compute='_compute_diacritics_insensitive_search',
        string="Diacritics insensitive search")

    @api.multi
    def _compute_diacritics_insensitive_search(self):
        ir_config_env = self.env['ir.config_parameter']
        value = safe_eval(ir_config_env.get_param(
            'diacritics_insensitive_search', 'False'))
        for record in self:
            record.diacritics_insensitive_search = value
