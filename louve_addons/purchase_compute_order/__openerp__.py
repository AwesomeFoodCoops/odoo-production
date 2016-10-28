# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
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
    'name': 'Computed Purchase Order',
    'version': '9.0.1',
    'category': 'Purchase',
    'description': """
Provide tools to help purchaser during purchase process
=======================================================

Functionnality :
----------------
    This module helps you to decide what you have to buy.

How To:
    * Create a new Compute Purchase Order (CPO)
    * Select a Supplier
    * Check the boxes to tell if you want to take into account the virtual
    stock or the draft sales/purchases
    * Use the button to import the list of products you can purchase to this
    supplier (ie: products that have a product_supplierinfo for this partner).
    It especially calculates for each product:
        * the quantity you have or will have;
        * the average_consumption, based on the stock moves created during
        last 365days;
        * the theorical duration of the stock, based on the precedent figures.

    * Unlink the products you don't want to buy anymore to this supplier
    (this only deletes the product_supplierinfo)
    *  Add new products you want to buy and link them
    (this creates a product_supplierinfo)
    * Modify any information about the products: supplier product_code,
    supplier product_name, purchase price, package quantity, purchase UoM.
    * Modify the calculated consumption if you think you'll sell more or
    less in the future.
    * Add a manual stock quantity (positive if you will receive products
    that are not registered at all in OE, negative if you have not registered
    sales)

    * Click the "Update Products" button to register the changes you've made
    into the product supplierinfo.
    * Check the Purchase Target. It's defined on the Partner form, but you
    still can change it on each CPO.
    * Click the button to calculate the quantities you should purchase. It
    will compute a purchase order fitting the purchase objective you set,
    trying to optimize the stock duration of all products.
    * Click the "Make Order" button to convert the calculation into a real
    purchase order.

Possible Improvements:
    * offer more options to calculate the average consumption;

Copyright, Author and Licence :
-------------------------------
    * Copyright : 2013-Today, Groupement Régional Alimentaire de Proximité;
    * Author :
        * Julien WESTE;
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'product_average_consumption',
        'purchase',
        'purchase_package_qty',
        'product_supplierinfo_discount',
    ],
    'data': [
        'data/ir_sequence.xml',
        'security/ir_rule_data.yml',
        'security/ir_model_access_data.yml',
        'wizard/update_product_wizard_view.xml',
        'views/action.xml',
        'views/view.xml',
        'views/menu.xml',
        'views/res_config_view.xml',
    ],
}
