# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: La Louve
# @author: Julien WESTE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Coop - Inventory',
    'version': '9.0.1.0.0',
    'category': 'Custom',
    'author': 'La Louve',
    'website': 'https://cooplalouve.fr',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'purchase_package_qty',
        'stock_inventory_by_category',
    ],
    'data': [
        'view/report_stockinventory.xml',
        'view/view_stock_inventory.xml',
        'view/view_stock_picking.xml',
    ],
}
