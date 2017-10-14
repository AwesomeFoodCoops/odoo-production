# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Bank auto reconcille',
    'version': '9.0.1',
    'category': 'Custom',
    'author': 'La Louve',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'pos_payment_terminal',
    ],
    'data': [
        'views/account_journal.xml',
        'views/account_bank_statement.xml',
    ],
}
