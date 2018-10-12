# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


{
    'name': 'Create Users From Partners',
    'version': '9.0.1.0.0',
    'category': 'Tools',
    'summary': 'Create Users On Partner Forms',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
    ],
    'data': [
        'security/res_groups.xml',


        # Views
        'views/res_partner_view.xml',
    ],
    'installable': True,
}
