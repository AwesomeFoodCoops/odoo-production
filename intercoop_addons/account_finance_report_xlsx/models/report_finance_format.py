# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, fields


class ReportFinanceFormat(models.TransientModel):
    _name = "report.finance.format"
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        'res.company',
        string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    format_report_finance = fields.Selection(
        [('pdf', 'PDF'), ('xlsx', 'XLSX')],
        string="Default format report finance",
        related="company_id.format_report_finance",
        default=lambda self: self.env.user.company_id.format_report_finance)
