
from odoo import api, models, _


class ShiftCounterEvent(models.Model):
    _inherit = "shift.counter.event"

    @api.model
    def cron_balance_counter(self, limit=1000):
        args = [
            ("display_std_points", "<", 0),
            ("display_ftop_points", ">", 0)
        ]
        partners = self.env["res.partner"].search(args, limit=limit)
        SCEvent = self.env['shift.counter.event'].sudo().with_context(
            automatic=True,
        )
        for partner in partners:
            points = min(abs(partner.display_std_points), partner.display_ftop_points)
            SCEvent.create([{
                'name': _('Equilibrage compteur Volant >>> Fixe'),
                'type': 'standard',
                'partner_id': partner.id,
                'point_qty': points,
            }, {
                'name': _('Equilibrage compteur Volant >>> Fixe'),
                'type': 'ftop',
                'partner_id': partner.id,
                'point_qty': points*-1,
            }])
