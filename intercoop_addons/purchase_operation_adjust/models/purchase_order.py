# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_view_picking(self):
        res = super(PurchaseOrder, self).action_view_picking()
        res['context'].update({
            'readonly_by_pass': True
        })
        return res
