##############################################################################
#
#    Sale - Food Module for Odoo
#    Copyright (C) 2012-Today GRAP (http://www.grap.coop)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
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
    "name": "Coop Default Price Tag",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "author": "GRAP," "Akretion - Julien WESTE," "Druidoo",
    "website": "http://www.grap.coop",
    "license": "AGPL-3",
    "depends": [
        "product",
        "product_print_category",
        "base",
        "purchase_package_qty",
        "uom",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_actions_report.xml",
        "data/report_paperformat.xml",
        "data/pricetag_model.xml",
        "data/product_category_print.xml",
        "report/coop_custom_product_report.xml",
        "report/report_pricetag.xml",
        "views/view_pricetag_model.xml",
        "views/view_product_label.xml",
        "views/view_product_product.xml",
        "views/view_product_template.xml",
        "views/view_product_uom_categ.xml",
        "views/action.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/res_groups.xml"
    ],
}
