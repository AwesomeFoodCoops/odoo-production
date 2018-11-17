# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Louve EDI Config',
    'version': '9.0.1.0.2',
    'category': 'Custom',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': ['purchase'
    ],
    'data': ['views/actions.xml',
             'views/menus.xml',
             'views/edi_config_system_view.xml',
             'views/purchase_edi_log_view.xml',
             'security/ir_module_category.xml',
             'security/res_groups.xml',
             'security/ir.model.access.csv',
    ],
}
