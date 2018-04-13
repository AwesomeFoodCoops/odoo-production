# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Account Deprecated',
    'version': '9.0.0.0.0',
    'category': 'Custom',
    'summary': 'Do not include deprecated accounts in search result',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'account',
    ],

    'data': [
        'views/actions.xml',
    ],

    'installable': True,
}
