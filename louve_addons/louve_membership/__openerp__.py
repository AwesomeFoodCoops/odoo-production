# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Louve - Membership',
    'version': '9.0.0.0.0',
    'category': 'Custom',
    'summary': 'Custom settings for membership in La Louve',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'capital_subscription',
        'coop_shift',
        'barcodes_generate',
    ],
    'data': [
        # Classical Data
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/action.xml',
        'views/view_res_partner.xml',
        'views/view_barcode_rule.xml',
        'views/view_account_invoice.xml',
        'views/view_capital_fundraising_wizard.xml',
        'views/view_capital_fundraising_category.xml',
        'views/view_res_partner_generate_barcode_wizard.xml',
        'views/menu.xml',

        # Custom Data
        'data/capital_fundraising_partner_type.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/barcode_rule.xml',
    ],
    'installable': True,
}
