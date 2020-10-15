# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reprint_change_field_ids = fields.Many2many(
        'ir.model.fields',
        string="Fields trigger badge reprinting",
        domain=[('model_id.model', '=', 'res.partner')],
    )

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        value = self.reprint_change_field_ids.ids
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('reprint_change_field_ids', value)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        field_str = self.env['ir.config_parameter'].sudo().get_param(
            'reprint_change_field_ids', '[]')
        field_ids = safe_eval(field_str)
        res.update(reprint_change_field_ids=field_ids)
        return res
