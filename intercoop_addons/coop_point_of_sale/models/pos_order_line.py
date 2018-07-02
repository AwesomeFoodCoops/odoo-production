# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api, fields, _
from datetime import datetime, timedelta
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    week_number = fields.Char(
        string='Week',
        related='order_id.week_number',
        store=True
    )
    week_day = fields.Char(
        string="Day",
        related='order_id.week_day',
        store=True
    )

    cycle = fields.Char(
        string="Cycle",
        related="order_id.cycle",
        store=True
    )

    @api.multi
    def compute_amount_line_all(self):
        """
        Util function that easily call _compute_amount_line_all from JSONRPC
        """
        self._compute_amount_line_all()
        return True
