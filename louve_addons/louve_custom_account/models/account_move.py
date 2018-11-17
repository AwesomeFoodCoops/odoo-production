# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def compute_move_type(self):
        super(AccountMove, self)._compute_move_type()
        return True
