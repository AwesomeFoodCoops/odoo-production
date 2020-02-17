# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


{
    "name": "POS Search Improvement",
    "version": "12.0.1.0.0",
    "category": "Point Of Sale",
    "summary": "Search Exactly Products",
    "author": "La Louve, Druidoo",
    "website": "http://www.lalouve.net",
    'license': 'AGPL-3',
    "depends": ["point_of_sale", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_product_view.xml",
        "static/src/xml/templates.xml",
    ],
    "installable": True,
}
