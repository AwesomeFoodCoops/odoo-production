# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class ShiftRegistration(models.Model):
    _inherit = "shift.registration"

    related_shift_state = fields.Selection(related="shift_id.state",
                                           store=False,
                                           string="Shift State")

    @api.multi
    @api.onchange("shift_id")
    def onchange_shift_id(self):
        # Use the context value for default
        is_standard_ticket = self.env.context.get("is_standard_ticket", False)
        ticket_type_product = False
        if is_standard_ticket:
            ticket_type_product = \
                self.env.ref("coop_shift.product_product_shift_standard")
        else:
            ticket_type_product = \
                self.env.ref("coop_shift.product_product_shift_ftop")
        for reg in self:
            reg.shift_ticket_id = reg.shift_id.shift_ticket_ids.filtered(
                lambda t: t.product_id == ticket_type_product)
