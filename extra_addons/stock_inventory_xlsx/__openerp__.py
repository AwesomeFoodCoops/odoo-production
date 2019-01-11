# -*- coding: utf-8 -*-

{
    'name': 'Stock Inventory Xlsx',
    'version': '9.0.1.0.0',
    'category': 'Custom',
    'summary': 'Stock Inventory Xlsx',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'report_xlsx',
        'stock_account',
    ],
    'data': [
        'report/report_inventory.xml',
        'wizard/stock_valuation_history_view.xml',
    ],
    'installable': True,
}
