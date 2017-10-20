# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.cooplalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
{
    'name': 'Coop Purchase',
    'version': '9.0.1.0.0',
    'category': 'Custom',
    'summary': 'Coop Purchase',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
        'account',
        'purchase',
        'purchase_package_qty',
        'purchase_compute_order',
        'coop_product_coefficient',
    ],
    'data': [
        'views/purchase_view.xml',
        'views/purchase_config_settings_view.xml',
        'views/actions.xml',
        'views/menu.xml'
    ],
    'installable': True,
}
