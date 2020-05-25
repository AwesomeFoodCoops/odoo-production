# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Coop - Membership',
    'version': '12.0.1.1.1',
    'category': 'Custom',
    'summary': 'Custom settings for membership',
    'author': 'La Louve, Druidoo',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'hr_maintenance',
        'project',
        'mass_mailing',
        'account_export',
        'account_partner_journal',
        'capital_subscription',
        'coop_shift',
        'purchase_compute_order',
        'res_partner_account_move_line',
        'stock',
        'partner_contact_birthdate',
    ],
    'data': [

        # Security
        'security/ir_module_category.xml',
        'security/res_group.xml',
        'security/ir.model.access.csv',
        'data/report_paperformat_data.xml',
        'data/ir_attachment.xml',
        'data/ir_config_parameter.xml',
        # Wizard
        'wizard/view_capital_fundraising_wizard.xml',
        'wizard/res_partner_generate_barcode_wizard.xml',
        # Classical Data
        'views/view_shift_counter_event.xml',
        'views/view_res_partner_owned_share.xml',
        'views/view_res_partner.xml',
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
        'views/event_view.xml',
        'views/event_config_settings_view.xml',
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
        'report/member_contract.xml',
        'report/member_contract_template.xml',

        # Custom Data
        'data/ir_cron.xml',
        'data/capital_fundraising_partner_type.xml',
        'data/email_template_data.xml',
        'data/ir_sequences.xml',
        'data/barcode_rule.xml',
        'data/res_partner_inform.xml',
        'data/shift_extension_type_data.xml',
        'data/function.xml',
    ],
    'demo': [
        'demo/capital_fundraising_category.xml',
        'demo/res_groups.xml',
    ],
    'installable': True,
    'application': True,
}
