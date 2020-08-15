# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class ShiftConfigSettings(models.TransientModel):
    _inherit = 'coop_shift.config.settings'

    @api.multi
    def action_recompute_shift_weeks(self):
        res = super(ShiftConfigSettings, self).action_recompute_shift_weeks()
        # Also recompute pos.orders and pos.sessions
        session = ConnectorSession(self._cr, self._uid)
        _job_recompute_week_number_pos_session.delay(session, None)
        _job_recompute_week_number_pos_order.delay(session, None)
        return res


@job
def _job_recompute_week_number_pos_session(session):
    recompute_week_number = \
        session.env['coop_shift.config.settings']._recompute_week_number
    # Update pos_session
    recompute_week_number(
        'pos_session', 'start_at', 'week_number', 'week_name')
    # Compute cycle
    session.env.cr.execute("""
        UPDATE pos_session
        SET cycle = CONCAT(week_name, week_day)
    """)


@job
def _job_recompute_week_number_pos_order(session):
    recompute_week_number = \
        session.env['coop_shift.config.settings']._recompute_week_number
    # Update pos_order
    recompute_week_number(
        'pos_order', 'date_order', 'week_number', 'week_name')
    session.env.cr.execute("""
        UPDATE pos_order
        SET cycle = CONCAT(week_name, week_day)
    """)
    # Update pos_order_line
    session.env.cr.execute("""
        UPDATE pos_order_line pol
        SET
            week_number = po.week_number,
            week_name = po.week_name,
            cycle = po.cycle
        FROM pos_order po
        WHERE pol.order_id = po.id
    """)
