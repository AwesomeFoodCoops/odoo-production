# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Account Reconcile Simple',
    'version': '9.0.0.0.0',
    'category': 'Accounting',
    'summary': 'Allow to reconcile only with the current journal accounts',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'account',
    ],
    'data': [
        "views/account_journal.xml",
    ],
    'installable': True,
}
