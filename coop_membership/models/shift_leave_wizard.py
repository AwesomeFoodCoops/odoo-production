# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class ShiftLeaveWizard(models.TransientModel):
    _inherit = 'shift.leave.wizard'

    @api.multi
    def button_confirm(self):
        self.ensure_one()

        leave = self.leave_id
        if not self._context.get('bypass_non_draft_confirm', False) and \
                leave.state != 'draft':
            raise ValidationError(_(
                "You can not confirm a leave in a non draft state."))

        if leave.non_defined_type and leave.non_defined_leave:
            leave.update_registration_template_based_non_define_leave()
        else:
            if leave.type_id.is_anticipated:
                leave.update_info_anticipated_leave()
            super(ShiftLeaveWizard, self).button_confirm()
