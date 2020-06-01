# -*- coding: utf-8 -*-
# Copyright (C) 2019: La Chouette Coop (https://lachouettecoop.fr)
# @author: La Chouette Coop
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import fields, models
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    weight_net = fields.Float(digits=dp.get_precision('Net Weight'))
    volume = fields.Float(digits=dp.get_precision('Volume'))

