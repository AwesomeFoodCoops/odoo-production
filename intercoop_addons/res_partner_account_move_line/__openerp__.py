# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Res Partner Account Move Line',
    'version': '9.0.0.0.0',
    'category': 'Base',
    'summary': 'Button to access partner\'s account move lines',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        "views/res_partner.xml",
    ],
    'installable': True,
}
