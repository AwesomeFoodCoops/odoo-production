# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.io/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_edi = fields.Boolean(string="Is an EDI supplier")
    is_prices_interface = fields.Boolean(string="Supports prices interface")
