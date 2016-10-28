# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product - Average Consumption Module for Odoo
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Product - History',
    'version': '9.0.2',
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
    ],
    'data': [
        'views/res_config_view.xml',
        'views/product_history_view.xml',
        'views/product_template_view.xml',
        'data/function.xml',
        'data/cron.xml',
        'security/ir_model_access_data.yml',
        'security/ir_rule_data.yml',
    ],
}
