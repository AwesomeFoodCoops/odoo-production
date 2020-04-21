# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)

{
    'name': 'Coop Account',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Coop Account',
    'author': 'La Louve, Druidoo',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'queue_job',
        'barcodes_generator_partner',
        'account_tax_balance',
    ],
    'data': [
        "view/assets.xml",
        "view/view_account_bank_statement.xml",
        "view/view_account_move.xml",
        "view/view_account_move_line.xml",
        "view/view_account_payment.xml",
        "view/view_account_account.xml",
        "view/view_account_invoice.xml",
        "wizard/view_bank_statement_line_reconcile_wizard.xml",
        "wizard/view_unmatch_bank_statement_wizard.xml",
        "view/menu.xml",
    ],
    'installable': True,
}
