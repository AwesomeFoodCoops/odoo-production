# -*- coding: utf-8 -*-
# Copyright (C) 2018-Today: La Louve (<https://cooplalouve.fr>)
# @author: Simon Mas (linkedin.com/in/simon-mas)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Coop Numerical Keyboard',
    'version': '9.0.1.0.0',
    'category': 'Tools',
    'summary': 'Create a new POS numerical keyboard',
    'author': 'Simon Mas, Phat Nguyen Tan, Odoo Community Association (OCA)',
    'website': 'https://www.druidoo.io',
    'depends': [
        'point_of_sale'
    ],
    'data': [
        # Views
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/widget.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
