# -*- coding: utf-8 -*-

from openerp import api, models
from openerp.exceptions import ValidationError


class ShiftLeaveWizard(models.TransientModel):
    _inherit = 'shift.leave.wizard'

    @api.multi
    def button_confirm(self):
        # Check
        for wiz in self:
            leave = wiz.leave_id
            if leave.is_parental_leave \
                and not leave.provide_birth_certificate \
                    and leave.start_before_birthday:
                raise ValidationError('Il faut un acte de naissance pour valider ce congé.')
        res = super(ShiftLeaveWizard, self).button_confirm()
        for wiz in self:
            leave = wiz.leave_id
            if leave.is_parental_leave:
                leave.send_validated_parental_leave_email()
        return res
