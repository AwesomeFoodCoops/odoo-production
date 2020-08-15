# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class ShiftConfigSettings(models.TransientModel):
    _inherit = 'coop_shift.config.settings'

    @api.multi
    def action_recompute_shift_weeks(self):
        res = super(ShiftConfigSettings, self).action_recompute_shift_weeks()
        # Also recompute pos.orders and pos.sessions
        _logger.info("Creating jobs to recompute week_name in pos.order..")
        self.env['pos.order'].with_context(
            active_test=False,
        ).search(
            [], order='id desc'
        )._recompute_week_fields_async()
        # PosSession
        _logger.info("Creating jobs to recompute week_name in pos.session..")
        self.env['pos.session'].with_context(
            active_test=False,
        ).search(
            [], order='id desc',
        )._recompute_week_fields_async()
        # Return message
        return res
