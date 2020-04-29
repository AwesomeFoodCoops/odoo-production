# Copyright 2019 Druidoo - Iván Todorovich
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "POS Order Wait Save",
    "version": "12.0.1.0.0",
    "category": "Point of Sale",
    "website": "https://www.druidoo.io",
    "author": "Druidoo",
    "license": "AGPL-3",
    "depends": [
        "point_of_sale",
    ],
    "data": [
        "views/assets.xml",
        "views/pos_config.xml",
    ],
    "qweb": [
        "static/src/xml/pos_ticket.xml",
    ],
    "installable": True,
}
