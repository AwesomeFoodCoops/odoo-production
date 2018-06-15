# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.multi
    def compute_amount_line_all(self):
        """
        Util function that easily call _compute_amount_line_all from JSONRPC
        """
        self._compute_amount_line_all()
        return True
