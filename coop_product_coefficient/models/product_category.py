# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# Copyright (C) 2012-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models


class ProductCategory(models.Model):
    _inherit = "product.category"
    _order = "name"
