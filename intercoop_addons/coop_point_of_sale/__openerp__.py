# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Coop - Point of Sale Custom views',
    'version': '9.0.2.0.0',
    'category': 'Custom',
    'summary': 'Customize Point of Sale Display',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'point_of_sale',
        'coop_membership',
    ],
    'qweb': [
        'static/src/xml/point_of_sale.xml',
    ],
    'data': [
        'static/src/xml/templates.xml',
        'views/view_pos_order.xml',
    ],
    'installable': True,
}
