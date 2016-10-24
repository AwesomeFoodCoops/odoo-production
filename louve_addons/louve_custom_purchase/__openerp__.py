# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
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
    'name': 'Louve Custom - Purchase',
    'version': '9.0',
    'category': 'Purchase',
    'description': """
Customize Purchase modules

Copyright, Author and Licence :
-------------------------------
    * Copyright : 2016, Akretion;
    * Author :
        * Julien WESTE;
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
        'product',
        'purchase_package_qty',
        'stock',
    ],
    'data': [
        'views/purchase_order_view.xml',
        'views/product_supplierinfo_view.xml',
        'views/report_purchaseorder.xml',
        'views/report_purchasequotation.xml',
        'views/stock_picking_view.xml',
    ],
}
