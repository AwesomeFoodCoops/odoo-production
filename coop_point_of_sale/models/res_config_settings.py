# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    def action_recompute_shift_weeks(self):
        res = super().action_recompute_shift_weeks()
        # Update pos_session
        self._recompute_week_number(
            'pos_session', 'start_at', 'week_number', 'week_name')
        # Compute cycle
        self.env.cr.execute("""
            UPDATE pos_session
            SET cycle = CONCAT(week_name, week_day)
        """)
        # Update pos_order
        self._recompute_week_number(
            'pos_order', 'date_order', 'week_number', 'week_name')
        self.env.cr.execute("""
            UPDATE pos_order
            SET cycle = CONCAT(week_name, week_day)
        """)
        # Update pos_order_line
        self.env.cr.execute("""
            UPDATE pos_order_line pol
            SET
                week_number = po.week_number,
                week_name = po.week_name,
                cycle = po.cycle
            FROM pos_order po
            WHERE pol.order_id = po.id
        """)
        return res
