# -*- encoding: utf-8 -*-
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
    'name': 'Product History for CPO',
    'version': '9.0.5',
    'category': 'Purchase',
    'description': """
Give access to Product History information in CPO process
=======================================================

Functionnality :
----------------
    In the cpo_line, a button can popup the product history. You can then
    see all history lines and mark some of them as "ignored".

Copyright, Author and Licence :
-------------------------------
    * Copyright : 2016-Today, Akretion;
    * Author :
        * Julien WESTE;
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/fr',
    'license': 'AGPL-3',
    'depends': [
        'purchase_compute_order',
        'product_history',
    ],
    'auto_install': True,
    'data': [
        'views/view.xml',
        'views/action.xml',
    ],
}
