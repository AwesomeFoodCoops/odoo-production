# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Bank auto reconcille',
    'version': '12.0.1.0.0',
    'category': 'Custom',
    'author': 'La Louve',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_journal.xml',
        'views/account_bank_statement.xml',
    ],
}
