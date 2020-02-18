# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Account Bank Statement Summary',
    'version': '9.0.1.0.11',
    'category': 'Account',
    'description': """
    """,

    'license': 'AGPL-3',
    'depends': [
        'report_xlsx', 'account'
    ],
    'data': [
        "report/report_bank_reconciliation_summary_view.xml",
        "wizard/view_bank_reconciliation_summary_wizard.xml",
    ],
}
