# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Point of Sale - Barcode Rule Transform',
    'version': '9.0.1.0.0',
    'category': 'Point Of Sale',
    'summary': 'Transforms the value read in the barcode with a JS expression',
    'author': 'Druidoo, Odoo Community Association (OCA)',
    'website': 'https://www.druidoo.io/',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/assets.xml',
        'views/barcode_rule.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
}
