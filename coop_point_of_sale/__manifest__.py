# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Coop - Point of Sale Custom views",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "summary": "Customize Point of Sale Display",
    "author": "La Louve, Druidoo",
    "website": "http://www.lalouve.net",
    'license': 'AGPL-3',
    "depends": [
        "point_of_sale",
        "coop_membership",
    ],
    "qweb": [
        "static/src/xml/point_of_sale.xml",
        "static/src/xml/popups.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/view_pos_order.xml",
        "views/view_res_config.xml",
        "views/view_pos_session.xml",
        "views/view_pos_order_line.xml",
        "views/view_pos_config_settings.xml",
        "views/view_pos_category.xml",
    ],
    "installable": True,
}
