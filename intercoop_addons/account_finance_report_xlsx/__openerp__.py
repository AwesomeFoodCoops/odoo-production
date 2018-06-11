# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Report Account Finance XLS',
    'version': '9.0.1.0.11',
    'category': 'Account',
    'description': """
    This module suports to print report finance with format XLSX
    """,

    'license': 'AGPL-3',
    'depends': [
        'report_xlsx', 'account',
    ],
    'data': [
        'report/report_account_finance_xlsx.xml',
        'views/report_finance_format_view.xml',
        'views/menu.xml',
    ],
}
