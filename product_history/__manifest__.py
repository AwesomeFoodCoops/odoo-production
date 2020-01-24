#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

{
    'name': 'Product - History',
    'version': '12.0.1.0.0',
    'category': 'Product',
    'description': """
Computes figures about the product's sales, purchases, stocks.
In menu Inventory/Settings, you can choose if this data will be displayed per
day/week/month.
===========================================================================
Possible improvements:
    Register history per location_id
    Add production_qty

Copyright, Author and Licence :
-------------------------------
    * Copyright : 2015-Today, Akretion;
    * Author :
        * Julien WESTE;
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/fr',
    'license': 'AGPL-3',
    'depends': [
        'product',
        'stock',
        'product_average_consumption',
        'connector',
    ],
    'data': [
        'security/product_history_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_view.xml',
        'views/product_history_view.xml',
        'views/product_template_view.xml',
        'data/function.xml',
        'data/cron.xml',
    ],
}
