# -*- coding: utf-8 -*-
# Copyright (C) 2018-Today: La Louve (<https://cooplalouve.fr>)
# @author: Simon Mas (linkedin.com/in/simon-mas)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Asset Management xlsx',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'summary': 'account_asset_management_xlsx',
    'author': 'Simon Mas,  Ân Lê Hoàng',
    'website': 'https://cooplalouve.fr',
    'depends': [
        'account',
        'account_asset',
        'report_xlsx',
    ],
    'data': [
        "report/report_account_asset_xlsx.xml",
        "security/ir.model.access.csv",
        "wizard/account_asset_xlsx_wizard.xml",
    ],
    'installable': True,
}
