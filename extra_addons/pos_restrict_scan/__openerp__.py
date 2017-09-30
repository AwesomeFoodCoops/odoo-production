# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'POS Restrict Scanning Product',
    'version': '9.0.7.0.0',
    'category': 'Point of Sale',
    'description': '''
        Restrict cashier from scanning product in non-product screen
    ''',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'static/src/xml/pos_template.xml',
    ],
    'demo': [],
}
