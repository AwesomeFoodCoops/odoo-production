# Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Coop Account Check Deposit',
    'version': '12.0.1.1.1',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'summary': 'Manage deposit of checks to the bank',
    'author': "Druidoo",
    'website': 'https://cooplalouve.fr/',
    'depends': [
        'account_check_deposit',
    ],
    'data': [
        'data/account_data.xml',
        'report/report_checkdeposit.xml',
        'views/account_deposit_view.xml',
        'views/account_journal_view.xml',
        'views/account_move_line_view.xml',
    ],
    'installable': True,
}
