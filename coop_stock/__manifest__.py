{
    "name": "Coop - Stock",
    "version": "12.0.1.1.0",
    "category": "Custom",
    "summary": "Custom settings for stock",
    "author": "La Louve, Druidoo",
    "website": "http://www.lalouve.net",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "stock_account",
        "stock_inventory_valuation_report",
        "point_of_sale",
        "purchase_package_qty",
        "queue_job",
    ],
    "data": [
        "views/action.xml",
        "views/menu.xml",
        "views/stock_picking_view.xml",
        "views/stock_inventory_valuation_report.xml",
    ],
    "installable": True,
}
