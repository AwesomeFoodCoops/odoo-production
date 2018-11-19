#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Coop Produce',
    'version': '9.0.1',
    'category': 'Warehouse',
    'sequence': 38,
    'description': """

    The module belongs the following features : 
        - Offer a simple form view to do stock inventory for vegetable and fruits. Quantities are based on default packaging of the product. 
        - An advanced form view to plan orders of the week  to send the supplier per day.

    """,
    'depends': [
        'base',
        'product',
        'stock',
        'purchase',
        'purchase_package_qty',
    ],
    'data': [
        # DATA
        'security/ir.model.access.csv',
        'data/decimal_precision.xml',

        #VIEWS
        'views/product_views.xml',
        'views/stock_views.xml',
        'views/templates.xml',
        'views/week_order_planning_view.xml',
        'wizard/show_product_history_view.xml',
        'wizard/stock_inventory_wizard.xml',

    ],
    'qweb': ['static/src/xml/widget.xml'],
}
