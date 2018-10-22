# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, fields


class res_company(models.Model):
    _inherit = "res.company"

    journal_config_ids = fields.Many2many(
        'account.journal',
        'rel_company_config_journal',
        'rel_account_journal_config',
        string="Cheques Journals",
        )

    payable_to = fields.Char(string="Payable to")
