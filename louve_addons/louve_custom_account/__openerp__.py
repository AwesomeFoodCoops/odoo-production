# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Louve Custom - Account',
    'version': '9.0.1.0.2',
    'category': 'Custom',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'barcodes_generate',
    ],
    'data': [
        'views/view_account_payment.xml',
        'views/view_account_invoice.xml',
    ],
}
