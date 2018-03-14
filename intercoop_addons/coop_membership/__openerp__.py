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
        'hr_equipment',
        'project',
        'mass_mailing',
        'account_export',
        'account_partner_journal',
        'barcodes_generate',
        'capital_subscription',
        'coop_capital_certificate',
        'coop_shift',
        'purchase_compute_order',
        'res_partner_account_move_line',
        'stock',
        'coop_base',
    ],
    'data': [
        # Security
        'security/ir_module_category.xml',
        'security/res_group.xml',
        'security/ir_model_access.yml',
        'security/ir.model.access.csv',

        # Wizard
        'wizard/view_capital_fundraising_wizard.xml',
        'wizard/res_partner_generate_barcode_wizard.xml',

        # Classical Data
        'views/view_res_partner_owned_share.xml',
        'views/view_res_partner.xml',
        'views/res_users_view.xml',
        'views/view_barcode_rule.xml',
        'views/view_account_invoice.xml',
        'views/view_capital_fundraising_category.xml',
        'views/view_shift_leave.xml',
        'views/view_shift_extension_type.xml',
        'views/view_shift_registration.xml',
        'views/view_shift_shift.xml',
        'views/res_config_view.xml',
	'views/view_shift_leave_type.xml',
        'views/account_view.xml',
        'views/capital_subscription_view.xml',
        'views/event_view.xml',
        'views/shift_view.xml',
        'views/view_shift_extension.xml',

        'views/action.xml',
        'views/menu.xml',

        # Custom Data
        'data/ir_cron.xml',
        'data/capital_fundraising_partner_type.xml',
        'data/email_template_data.xml',
        'data/ir_sequences.xml',
        'data/barcode_rule.xml',
        'data/shift_extension_type_data.xml',

        # Report
        'views/account_report.xml',
    ],
    'demo': [
        'demo/capital_fundraising_category.xml',
        'demo/res_groups.xml',
    ],
    'installable': True,
}
