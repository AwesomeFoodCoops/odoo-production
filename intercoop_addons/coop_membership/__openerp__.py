# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Coop - Membership',
    'version': '9.0.3.0.0',
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
        'email_pos_receipt',
        'create_users_partners',
        'l10n_fr_pos_cert_base',
        'purchase_discount',
        'hr_skill',
    ],
    'data': [
        'data/update_template_name_ftop.yml',
        'data/update_menu_user_right.yml',
        'data/report_paperformat_data.xml',
        'data/ir_attachment.xml',
        'data/ir_config_parameter.xml',



        # Security
        'security/ir_module_category.xml',
        'security/res_group.xml',
        'security/ir_model_access.yml',
        'security/ir.model.access.csv',

        # Wizard
        'wizard/view_capital_fundraising_wizard.xml',
        'wizard/res_partner_generate_barcode_wizard.xml',
        'wizard/shift_template_evacuate_wizard.xml',

        # Classical Data
        'views/view_shift_counter_event.xml',
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
        'views/event_config_settings_view.xml',
        'views/shift_view.xml',
        'views/view_shift_extension.xml',
        'views/view_shift_ticket.xml',
        'views/event_registration_view.xml',
        'views/web_templates.xml',
        'views/view_web_access_buttons.xml',
        'views/view_shift_holiday.xml',
        'views/custom_templates.xml',
        'views/view_shift_change_team.xml',
        'views/view_shift_template.xml',
        'views/view_mass_mailling.xml',
        'views/view_shift_credit_config.xml',
        'views/action.xml',
        'views/menu.xml',

        'report/member_contract_template.xml',

        # Custom Data
        'data/ir_cron.xml',
        'data/capital_fundraising_partner_type.xml',
        'data/email_template_data.xml',
        'data/ir_sequences.xml',
        'data/barcode_rule.xml',
        'data/res_partner_inform.xml',
        'data/shift_extension_type_data.xml',
        'data/ir_config_paramater.xml',

        # Report
        'views/account_report.xml',

        # Custom function
        # 'data/function.xml',
    ],
    'demo': [
        'demo/capital_fundraising_category.xml',
        'demo/res_groups.xml',
    ],
    'installable': True,
}
