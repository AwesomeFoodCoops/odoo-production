
{
    'name': 'Coop Produce',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'summary': 'Coop Produce',
    'author': 'La Louve, Druidoo',
    'website': "http://www.lalouve.net",
    'license': 'AGPL-3',
    'description': """
        The module belongs the following features :
        -   Offer a simple form view to do stock inventory for vegetable and fruits.
        Quantities are based on default packaging of the product.
        -   An advanced form view to plan orders of the week
        to send the supplier per day.
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

        # VIEWS
        'views/product_views.xml',
        'views/stock_views.xml',
        'views/week_order_planning_view.xml',
        'views/templates.xml',
        'wizard/show_product_history_view.xml',
        'wizard/stock_inventory_wizard.xml',
    ],
}
