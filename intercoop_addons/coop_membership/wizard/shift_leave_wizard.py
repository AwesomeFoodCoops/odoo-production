# -*- coding: utf-8 -*-

from openerp import api, models


class ShiftLeaveWizard(models.TransientModel):
    _inherit = 'shift.leave.wizard'

    @api.multi
    def button_confirm(self):
        res = super(ShiftLeaveWizard, self).button_confirm()
        tmpl_name = self._context.get('leave_mail_tmpl', False)

        for wiz in self:
            leave = wiz.leave_id
            if not (leave.type_id and leave.type_id.is_temp_leave):
                continue
            if not tmpl_name:
                tmpl_name = leave.partner_id.in_ftop_team and \
                    'coop_membership.coop_ftop_leave_email' or \
                    'coop_membership.coop_abcd_leave_email'

            mail_tmpl = self.env.ref(tmpl_name)
            if mail_tmpl:
                mail_tmpl.send_mail(leave.id)

        return res

