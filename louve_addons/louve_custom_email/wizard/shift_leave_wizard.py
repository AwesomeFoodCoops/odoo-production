# -*- coding: utf-8 -*-

from openerp import api, models


class ShiftLeaveWizard(models.TransientModel):
    _inherit = 'shift.leave.wizard'

    @api.multi
    def button_confirm(self):
        tmpl_name = False
        for wiz in self:
            tmpl_name = wiz.partner_id.in_ftop_team and \
                'louve_custom_email.louve_ftop_leave_email' or \
                'louve_custom_email.louve_abcd_leave_email'
        return super(ShiftLeaveWizard, self.with_context(
            leave_mail_tmpl=tmpl_name)).button_confirm()
