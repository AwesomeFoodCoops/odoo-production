# -*- coding: utf-8 -*-
##############################################################################
#
#    Sale - Food Module for Odoo
#    Copyright (C) 2012-Today GRAP (http://www.grap.coop)
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
    'name': 'Louve Custom - Extra Information for Products',
    'version': '9.0.0.0.0',
    'category': 'Custom',
    'description': """
Functionnalities

* Add various information about origin, makers, etc...
    """,
    'author': 'GRAP,'
              'Akretion - Julien WESTE',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'coop_default_pricetag',
        'report',
    ],
    'data': [
        'data/ir_actions_report_xml.xml',
        'data/report_paperformat.xml',
        'data/pricetag_model.xml',
        'data/product_category_print.xml',
        'report/louve_custom_product_report.xml',
        'report/report_pricetag_vegetables.xml',
    ],
    'demo': [
    ],
    'css': [
        'static/src/css/pricetag_vegetables.css',
    ],
}
