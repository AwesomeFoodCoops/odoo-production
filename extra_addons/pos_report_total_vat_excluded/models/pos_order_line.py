# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste (julien.weste@akretion.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    price_subtotal = fields.Float(store=True)
    price_subtotal_incl = fields.Float(store=True)
