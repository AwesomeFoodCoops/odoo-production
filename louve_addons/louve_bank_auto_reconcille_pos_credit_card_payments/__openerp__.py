# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Louve bank auto reconcille',
    'version': '9.0.1',
    'category': 'Custom',
    'author': 'Smile',
    'website': 'http://www.smile.fr',
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
