# -*- coding: utf-8 -*-
# Copyright (C) 2015-Today: Smile (<http://www.smile.fr>)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Coop Product Coefficient',
    'version': '1.0',
    'summary': 'Coop Product Coefficients',
    'author': 'La Louve,Smile',
    'website': 'http://www.lalouve.net',
    'category': 'Product',
    'depends': [
        'product_supplierinfo_discount',
        'account',
        'coop_shift'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/view_product_template.xml',
        'views/view_product_product.xml',
        'views/view_product_coefficient.xml',
        'views/view_wizard_use_theoritical_price.xml',
        'views/view_sale_config_settings.xml',
        'views/action.xml',
        'views/menu.xml',
        'data/ir_cron.xml',
        'data/sale_config_settings.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/product.coefficient.csv',
        'demo/product_template.xml',
    ],
    'installable': True,
   # 'pre_init_hook': '_migration_script',
}
