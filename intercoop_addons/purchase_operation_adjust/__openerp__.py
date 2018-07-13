# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Purchase Stock Operation Adjustment',
    'version': '9.0.1.0.11',
    'category': 'Purchase',
    'description': """
        Generate purchase order line to matched with stock pack operation that
        were added manually from stock picking
        To create a right invoice has invoice line that matched with purchase
        order line and stock pack operations
    """,

    'license': 'AGPL-3',
    'depends': [
        'purchase_package_qty',
    ],
    'data': [
    ],
}
