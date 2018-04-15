# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)


{
    'name': 'Coop Account',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Coop Account',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'account', 'account_asset'
    ],
    'data': [
        "data/ir_cron.xml",
        "security/res_group.xml",
        "view/view_account_config_setting.xml",
        "view/view_account_bank_statement.xml",
        "view/view_account_move.xml",
        "view/view_account_move_line.xml",
        "view/view_account_payment.xml",
        "view/view_account_asset_asset.xml",
        "view/view_account_account.xml",
        "wizard/view_bank_statement_line_reconcile_wizard.xml",
    ],
    'installable': True,
}
