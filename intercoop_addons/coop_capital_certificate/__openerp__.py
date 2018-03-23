# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Coop Capital Certificate',
    'version': '9.0.0.0.0',
    'category': 'Accounting',
    'summary': 'Provide a Fiscal Certificate report for capital subscriptions',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'capital_subscription',
    ],
    'data': [
        'report/coop_capital_certificate_report.xml',
        'report/report_capital_certificate.xml',
        'data/email_template_data.xml',
        'security/ir_model_access.yml',
        'wizard/view_capital_certificate.xml',
        'views/account_config_settings.xml',
        'views/view_capital_certificate.xml',
        'views/view_res_partner.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
