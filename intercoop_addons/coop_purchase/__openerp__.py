# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.cooplalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
{
    'name': 'Coop Purchase',
    'version': '9.0.1.0.0',
    'category': 'Custom',
    'summary': 'Coop Purchase',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
        'account',
        'product',
        'purchase',
        'purchase_package_qty',
        'purchase_compute_order',
        'stock',
        'coop_product_coefficient',
        'account_product_fiscal_classification',
        'l10n_fr_pos_cert_base',
    ],
    'data': [
        'security/res_group.xml',
        'views/purchase_view.xml',
        'views/purchase_config_settings_view.xml',
        'views/account_invoice_view.xml',
        'views/account_product_fiscal_classification_view.xml',
        'views/product_template_view.xml',
        'views/product_supplierinfo_view.xml',
        'views/report_purchaseorder.xml',
        'views/report_purchasequotation.xml',
        'views/actions.xml',
        'views/menu.xml',
        'views/stock_picking_view.xml',
        'wizard/supplier_info_update.xml',
    ],
    'installable': True,
}
