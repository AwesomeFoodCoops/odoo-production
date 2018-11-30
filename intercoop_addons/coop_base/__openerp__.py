# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<https://cooplalouve.fr>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Coop Base',
    'version': '9.0.1.0.0',
    'category': '',
    'summary': 'Coop Base',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base'     
    ],
    'data': [
        "data/res_group_data.xml",

        # security
        "security/ir.model.access.csv",
        
        # menu
        "menu/admin_menu.xml",

        # Post function
        "data/function.xml",
    ],
    'installable': True,
}
