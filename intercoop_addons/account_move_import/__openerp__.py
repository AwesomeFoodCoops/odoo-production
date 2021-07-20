# -*- coding: utf-8 -*-

{
    'name': 'Import Account Moves',
    'version': '9.0.1.0.0',
    'category': 'Tools',
    'summary': 'Import Account Move from .csv files',
    'author': 'Druidoo',
    'website': 'https://www.druidoo.io',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',

        # Views
        'wizard/wizard_account_move_import.xml',
        'views/account_move_import_history_views.xml',

        #Data
        'data/account_journal_data.xml'
    ],
    'external_dependencies': {
        'python': [
            'xlrd',
        ],
    },
    'installable': True,
    'license': 'AGPL-3',
}
