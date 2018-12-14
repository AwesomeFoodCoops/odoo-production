# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)


{
    'name': 'Account Asset Management Xlsx',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'summary': 'account_asset_management_xlsx',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
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
