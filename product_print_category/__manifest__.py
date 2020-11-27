# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product - To Print",
    "summary": "Automate products print, when data has changed",
    "version": "12.0.1.0.0",
    "category": "Product",
    "license": "AGPL-3",
    "author": "GRAP, Druidoo",
    "depends": ["product", "sale"],
    "demo": [
        "demo/res_groups.xml",
        "demo/qweb_template.xml",
        "demo/product_print_category.xml",
        "demo/product_product.xml",
    ],
    "data": [
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/report_paperformat.xml",
        "report/report_pricetag.xml",
        "report/ir_actions_report.xml",
        "wizard/view_product_print_wizard.xml",
        "views/view_product.xml",
        "views/view_res_company.xml",
        "views/action.xml",
        "views/view_product_print_category.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
