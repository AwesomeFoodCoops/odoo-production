# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Cagette (<http://www.lacagette.net/>)
# @author: La Cagette
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Cagette - Print Badge',
    'version': '9.0.1.0.11',
    'category': 'Custom',
    'summary': 'Print Cagette partner\'s badge',
    'author': 'La Cagette',
    'website': 'http://www.lacagette.net',
    'depends': [
        'coop_print_badge',
    ],
    'data': [
        'data/report_paperformat.xml',
        'report/cagette_print_badge_report.xml',
        'report/report_printbadge.xml',
    ],
    'css': [
        'static/src/css/badge.css',
    ],
    'installable': True,
}
