# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Coop - Print Badge',
    'version': '12.0.1.0.0',
    'category': 'Custom',
    'summary': 'Print partner\'s badge',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
        'web',
        'barcodes_generator_abstract',
        'barcodes_generator_partner',
        'barcodes_generator_product',
        'coop_shift',
        'coop_membership',
        'coop_capital_certificate',
    ],
    'data': [
        'security/res_groups.xml',
        'data/report_paperformat.xml',
        'views/view_res_partner.xml',
        'views/badge_to_print_views.xml',
        'views/res_config_settings_view.xml',
        'views/actions.xml',
        'views/menu.xml',
        'report/coop_print_badge_report.xml',
        'report/report_printbadge.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
