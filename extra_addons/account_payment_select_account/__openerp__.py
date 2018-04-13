# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Account Payment - Select Account',
    'version': '9.0.7.0.0',
    'category': 'Accounting & Finance',
    'description': '''
        Allow user to select the account on Register Payment of Invoice if
        the default Debit / Credit account is not set in the selected Journal
    ''',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_payment_view.xml',
    ],
    'demo': [],
}
