# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author Cyril GASPARD
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Coop Shift',
    'version': '9.0.9.0.0',
    'category': 'Tools',
    'author': 'Julien WESTE, Sylvain LE GAL, Cyril Gaspard, La Louve',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'event',
        'event_sale',
        'mail',
        'barcodes_generate',
        'connector',
        'web',
    ],
    'data': [
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/function.xml',
        'data/coop_shift_data.xml',
        'views/action.xml',
        'wizard/create_shifts_wizard_view.xml',
        'wizard/update_shifts_wizard_view.xml',
        'wizard/add_template_registration_view.xml',
        'wizard/replace_registration_view.xml',
        'data/email_template_data.xml',
        'views/menu.xml',
        'wizard/report_timesheet_wizard_view.xml',
        'wizard/report_wallchart_wizard_view.xml',
        'views/product_view.xml',
        'views/shift_mail_view.xml',
        'views/shift_registration_view.xml',
        'views/shift_template_registration_view.xml',
        'views/shift_template_registration_line_view.xml',
        'views/shift_shift_view.xml',
        'views/shift_template_view.xml',
        'wizard/create_shifts_wizard_view2.xml',
        'views/shift_type_view.xml',
        'views/shift_ticket_view.xml',
        'views/view_shift_counter_event.xml',
        'views/res_partner_view.xml',
        'views/view_res_partner.xml',
        'views/view_shift_extension.xml',
        'views/view_shift_extension_type.xml',
        'views/view_shift_leave.xml',
        'views/view_shift_leave_type.xml',
        'views/view_shift_leave_wizard.xml',
        'data/module_data.xml',
        'data/report_paperformat.xml',
        'views/report_layout_custom.xml',
        'views/shift_report.xml',
        'views/shift_report2.xml',
        'views/report_timesheet.xml',
        'views/report_timesheet_inherited.xml',
        'views/report_wallchart.xml',
        'views/ir_ui_menu_view.xml',
        'data/cron.xml',
        'data/ir_cron.xml',
    ],
    'qweb': ['static/src/xml/base.xml'],
    'demo': [
        'demo/res_groups.xml',
        'demo/res_partner.xml',
        'demo/shift_template.xml',
        # 'demo/shift_template_registration.xml',
    ],
}
