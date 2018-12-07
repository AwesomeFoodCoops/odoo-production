# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<https://cooplalouve.fr>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'l10n_fr_pos_cert_base',
    'version': '9.0.1.0.0',
    'category': '',
    'summary': 'l10n_fr_pos_cert_base',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
    ],
    'data': [
        # data
        "data/res_group_data.xml",

        # security
        "security/ir.model.access.csv",

        # views
        "views/view_user_config_settings.xml",
        "views/templates.xml",
        
        # menu
        "menu/admin_menu.xml",
    ],
    'qweb': ['static/src/xml/widget.xml'],
    'installable': True,
}
