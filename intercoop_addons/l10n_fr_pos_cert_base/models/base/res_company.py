# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp import SUPERUSER_ID


class ResCompany(models.Model):
    _inherit = "res.company"

    configuration_user_ids = fields.Many2many(
        comodel_name='res.users'
    )
