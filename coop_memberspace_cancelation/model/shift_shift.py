
from odoo import models, api, _


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    @api.multi
    def button_done(self):
        """
        @Overide the function to create -1 point counter for standard registration
        which is canceled
        """
        super(ShiftShift, self).button_done()
        SCEvent = self.env['shift.counter.event'].sudo().with_context(
            automatic=True,
        )
        for shift in self:
            for record in shift.registration_ids:
                if record.state == "cancel" and record.shift_type == "standard":
                    vals = {
                        'name': _('Annuler votre participation'),
                        'type': 'standard',
                        'partner_id': record.partner_id.id,
                        'point_qty': -1,
                        'shift_id': record.shift_id.id
                    }
                    if record.partner_id.final_ftop_point > 0:
                        vals["type"] = "ftop"
                    SCEvent.create(vals)
