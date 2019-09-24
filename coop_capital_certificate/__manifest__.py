# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Coop Capital Certificate',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Provide a Fiscal Certificate report for capital subscriptions',
    'author': 'La Louve, Druidoo',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'capital_subscription',
    ],
    'data': [
        'report/coop_capital_certificate_report.xml',
        'report/report_capital_certificate.xml',
        'data/email_template_data.xml',
        'security/ir.model.access.csv',
        'wizard/view_capital_certificate.xml',
        'views/res_config_settings_view.xml',
        'views/view_capital_certificate.xml',
        'views/view_res_partner.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
