# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    @author Julien WESTE
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
    'name': 'Louve Custom - Pricetags',
    'version': '9.0.0.0.0',
    'category': 'Sales',
    'description': """
Customize louve_custom_product module

Copyright, Author and Licence :
-------------------------------
    * Copyright : 2016, Akretion;
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'Julien WESTE - Akretion',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'depends': [
        'louve_custom_product',
        'purchase_package_qty',
        'l10n_fr_department',
    ],
    'data': [
        'data/report_paperformat.xml',
        'data/pricetag_model.xml',
        'data/product_category_print.xml',
        'report/louve_custom_pricetag_report.xml',
        'report/report_pricetag.xml',
        'report/report_pricetag_vegetables.xml',
        'views/view_product_template.xml',
        'views/view_product_category_print.xml',
    ],
    'css': [
        'static/src/css/pricetag_vegetables.css',
    ],
}
