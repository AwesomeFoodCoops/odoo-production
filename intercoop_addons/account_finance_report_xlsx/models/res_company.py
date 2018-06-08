# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, fields


class res_company(models.Model):
    _inherit = "res.company"

    format_report_finance = fields.Selection(
        [('pdf', 'PDF'), ('xlsx', 'XLSX')],
        string="Default format report finance",
    )
