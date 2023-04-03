# Copyright 2019-2020 Coop IT Easy SCRLfs
# 	    Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Require Product To Be Scaled in POS",
    "version": "12.0.1.0.0",
    "author": "Trobz",
    "website": "https://www.trobz.com",
    "license": "AGPL-3",
    "category": "Point of Sale",
    "summary": """
        A popup is shown if product need to weight with scale for one or more order
        lines when clicking on "Payment" button.
    """,
    "depends": [
        'point_of_sale',
    ],
    'data': [
        'views/pos_config.xml',
        'views/assets.xml',
    ],
    'installable': True,
}
