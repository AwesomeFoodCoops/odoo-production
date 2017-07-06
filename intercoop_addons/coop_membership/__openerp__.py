# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Coop - Membership',
    'version': '9.0.2.0.0',
    'category': 'Custom',
    'summary': 'Custom settings for membership',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'capital_subscription',
        'coop_shift',
        'barcodes_generate',
    ],
    'data': [
        # Classical Data
        'views/action.xml',
        'views/view_res_partner_owned_share.xml',
        'views/view_res_partner.xml',
        'views/view_barcode_rule.xml',
        'views/view_account_invoice.xml',
        'views/view_capital_fundraising_category.xml',
        'views/view_res_partner_generate_barcode_wizard.xml',
        'views/view_shift_leave.xml',
        'views/menu.xml',

        # Custom Data
        'data/ir_cron.xml',
        'data/capital_fundraising_partner_type.xml',
        'data/email_template_data.xml',
        'data/ir_sequences.xml',
        'data/barcode_rule.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/capital_fundraising_category.xml',
    ],
    'installable': True,
}
