# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models


class ProductLabel(models.Model):
    _inherit = 'product.label'

    scale_logo_code = fields.Char(string="Scale Logo Code")
