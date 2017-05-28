# -*- coding: utf-8 -*-

from openerp import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        '''
        Function trigger to
            - Change the email of current user to the email of
            the assigned partner
        '''
        self.login = self.partner_id and self.partner_id.email or ''
