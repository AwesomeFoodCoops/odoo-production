# -*- coding: utf-8 -*-
# Copyright (C) 2018-Today: La Louve (<https://cooplalouve.fr>)
# @author: Simon Mas (linkedin.com/in/simon-mas)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).



{
    'name': 'Create Users From Partners',
    'version': '9.0.1.0.0',
    'category': 'Tools',
    'summary': 'Create Users Action On Partner Forms',
    'author': 'Simon Mas, An Le Hoang, Odoo Community Association (OCA)',
    'website': 'https://www.druidoo.io',
    'depends': [
        'base',
    ],
    'data': [
        'security/res_groups.xml',


        # Views
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
