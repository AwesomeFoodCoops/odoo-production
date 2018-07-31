# -*- coding: utf-8 -*-

from openerp import models, api
from openerp.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_warning_member_state(self):
        IrConfig  = self.env['ir.config_parameter']
        warning_member_state = safe_eval(IrConfig.sudo().get_param(
            'warning_member_state'))
        if not (self.cooperative_state and warning_member_state.has_key(
            self.cooperative_state)):
            return warning_member_state['none']['alert'] + ' ' + \
                warning_member_state['none']['message']
        return warning_member_state[self.cooperative_state]['alert'] + ' ' + \
            warning_member_state[self.cooperative_state]['message']
            