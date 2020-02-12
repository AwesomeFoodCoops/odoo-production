# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Coop Default Price Tag",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "author": "GRAP, Akretion - Julien WESTE, Druidoo",
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
