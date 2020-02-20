from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ShiftLeaveWizard(models.TransientModel):
    _inherit = "shift.leave.wizard"

    @api.multi
    def button_confirm(self):
        # Check
        for wiz in self:
            leave = wiz.leave_id
            today_dt = fields.Date.today()
            if leave.is_parental_leave and not \
                    leave.provided_birth_certificate and \
                    leave.expected_birthdate < today_dt:
                raise ValidationError(_(
                    "Il faut un acte de naissance pour valider ce congé."
                ))
        res = super(ShiftLeaveWizard, self).button_confirm()
        for wiz in self:
            leave = wiz.leave_id
            if leave.is_parental_leave:
                leave.send_validated_parental_leave_email()
        return res
