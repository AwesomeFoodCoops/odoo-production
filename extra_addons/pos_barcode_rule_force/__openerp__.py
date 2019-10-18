# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Point of Sale - Barcode Rule Force',
    'version': '9.0.1.0.0',
    'category': 'Point Of Sale',
    'summary': 'On the product template, allow to force a specific rule',
    'author': 'Druidoo, Odoo Community Association (OCA)',
    'website': 'https://www.druidoo.io/',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
        'pos_barcode_rule_transform',  # because of the hooks
    ],
    'data': [
        'views/assets.xml',
        'views/product_template.xml',
    ],
    'installable': True,
}
