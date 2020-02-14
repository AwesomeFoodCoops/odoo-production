# © 2010-2011 Elico Corp. All Rights Reserved.
# Author: Ian Li <ian.li@elico-corp.com>
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Merge Wizard',
    'version': '12.0.1.0.0',
    'category': 'Finance',
    'author': "Elico Corp, Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/account-invoicing/',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'wizard/invoice_merge_view.xml',
    ],
    'installable': True,
}
