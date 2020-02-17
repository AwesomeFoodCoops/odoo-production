# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


{
    'name': 'Coop Limit Creation of Product',
    'version': '9.0.1.0.0',
    'category': 'Product',
    'description': """
        Module prevent the action that create product quickly from some views 
        like purchase order lines, invoice lines, sale order lines ...
    """,
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'sale', 'purchase', 'account', 'account_voucher', 'stock',
    ],
    'data': [
        'views/view_account_invoice.xml',
        'views/view_purchase_order.xml',
        'views/view_account_voucher.xml',
        'views/view_sale_order.xml',
        'views/view_stock_picking.xml',
        'views/view_stock_move.xml',
    ],
    'installable': True,
}
