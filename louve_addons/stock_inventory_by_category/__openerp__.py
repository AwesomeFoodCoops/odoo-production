# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Inventory by Category',
    'version': '9.0.0.0.0',
    'category': 'Stock',
    'summary': 'Allow to make inventory on selected categories',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'stock',
    ],
    'data': [
        'views/view_stock_inventory.xml',
    ],
    'installable': True,
}
