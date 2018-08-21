# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import models, fields, api, _
import logging
import random
_logger = logging.getLogger(__name__)
from openerp.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    is_print_receipt = fields.Boolean(
        string="Print receipt when not sent email",
        default=False)
