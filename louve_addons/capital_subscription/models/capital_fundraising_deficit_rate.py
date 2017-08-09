# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models


class CapitalFundraisingDeficitShare(models.Model):
    _name = 'capital.fundraising.deficit.rate'

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    percentage = fields.Float("Percentage")
