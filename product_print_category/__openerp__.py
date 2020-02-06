# coding: utf-8
# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product - To Print',
    'summary': 'Automate products print, when data has changed',
    'version': '8.0.2.0.0',
    'category': 'Product',
    'license': 'AGPL-3',
    'author': 'GRAP,La Louve',
    'depends': [
        'product',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/qweb_template.xml',
        'demo/product_print_category.xml',
        'demo/product_product.xml',
    ],
    'data': [
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'report/report_pricetag.xml',
        'report/ir_actions_report_xml.xml',
        'wizard/view_product_print_wizard.xml',
        'views/view_product_product.xml',
        'views/view_product_template.xml',
        'views/view_res_company.xml',
        'views/action.xml',
        'views/view_product_print_category.xml',
        'views/menu.xml',
    ],
    'installable': False,
}
