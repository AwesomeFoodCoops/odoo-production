# Copyright (C) 2025-Today: Trobz (<http://www.trobz.com/>)

{
    "name": "POS Order Line Removal",
    "version": "12.0.1.0.0",
    "category": "Point Of Sale",
    "summary": "Remove order lines from the POS interface",
    "author": "Trobz",
    "website": "http://www.trobz.com",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "static/src/xml/templates.xml",
        "views/pos_config.xml",
    ],
    'qweb': [
        'static/src/xml/order_line.xml'
    ],
    "installable": True,
}
