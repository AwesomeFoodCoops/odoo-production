# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'coop_shift.config.settings'

    reprint_change_field_ids = fields.Many2many(
        'ir.model.fields', string="Fields trigger badge reprinting",
        domain=[('model_id.model', '=', 'res.partner')])

    @api.multi
    def set_params(self):
        self.ensure_one()
        value = self.reprint_change_field_ids.ids
        self.env['ir.config_parameter'].set_param(
            'reprint_change_field_ids', value)

    @api.multi
    def get_default_params(self):
        field_str = self.env['ir.config_parameter'].get_param(
            'reprint_change_field_ids', '[]')
        field_ids = safe_eval(field_str)
        return {
            'reprint_change_field_ids': field_ids
        }
