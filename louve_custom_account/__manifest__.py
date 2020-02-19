# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Louve Custom - Account',
    'version': '12.0.1.0.0',
    'category': 'Custom',
    'author': 'La Louve, Druidoo',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'barcodes_generator_product',
        'account_tax_balance',
    ],
    'data': [
        'security/res_group.xml',
        'security/ir.model.access.csv',
        'views/view_account_payment.xml',
        'views/view_account_invoice.xml',
        'views/view_account_move_line.xml',
    ],
}
