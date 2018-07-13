# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


from openerp import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    operation_extra_id = fields.Many2one(
        'stock.pack.operation',
        string="Pack Operation Extra",
        help="The technical field is use to specify the line" +
        " that was generated from adding operation pack manually")
