# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Coop - Print Badge',
    'version': '9.0.1.0.0',
    'category': 'Custom',
    'summary': 'Print partner\'s badge',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
        'barcodes_generate',
        'report',
    ],
    'data': [
        'data/report_paperformat.xml',
        'report/coop_print_badge_report.xml',
        'report/report_printbadge.xml',
    ],
    'css': [
        'static/src/css/badge.css',
    ],
    'installable': True,
}
