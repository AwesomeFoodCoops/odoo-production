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
    'name': 'Coop Default Price Tag',
    'version': '9.0.1.0.11',
    'category': 'Custom',
    'description': """
Functionnalities
  - Showing a new tab `Food Informations` on product form view.
  - Default price tag for products with its management by user's right.
    """,
    'author': 'GRAP,'
              'Akretion - Julien WESTE',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'product',
        'product_to_print',
        'report',
        'l10n_fr_department',
        'purchase_package_qty',
    ],
    'data': [
        'security/res_groups.yml',
        'security/ir.model.access.csv',
        'data/ir_actions_report_xml.yml',
        'data/report_paperformat.xml',
        'data/pricetag_model.xml',
        'data/product_category_print.xml',
        'report/coop_custom_product_report.xml',
        'report/report_pricetag.xml',
        'views/view_product_label.xml',
        'views/view_product_product.xml',
        'views/view_product_template.xml',
        'views/view_product_uom_categ.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/res_groups.yml',
    ],
    'css': [
        'static/src/css/pricetag.css',
    ],
}
