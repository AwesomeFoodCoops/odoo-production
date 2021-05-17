# Copyright 2016-2018 Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# Copyright 2018 Lambda IS DOOEL <https://www.lambda-is.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Point of Sale Order Scrap',
    'version': '12.0.1.0.0',
    'category': 'Point Of Sale',
    'author': 'Trobz',
    'license': 'AGPL-3',
    'depends': [
        'pos_order_return',
    ],
    'data': [
        'wizard/pos_partial_return_wizard_view.xml',
    ],
    'installable': True,
}
