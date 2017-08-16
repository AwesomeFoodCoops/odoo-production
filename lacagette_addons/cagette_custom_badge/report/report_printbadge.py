# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Cagette (<http://www.lacagette.net/>)
# @author: La Cagette
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ReportPrintbadge(models.AbstractModel):
    _name = 'report.cagette_custom_badge.report_printbadge'
    _inherit = 'report.coop_print_badge.report_printbadge'

    # define image size as a tuple(width, height)
    img_size = tuple([30, 39])
