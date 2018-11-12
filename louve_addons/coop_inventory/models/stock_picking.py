# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_ref = fields.Char(string="Partner Ref",
                              related="purchase_id.partner_ref",
                              readonly=True)
