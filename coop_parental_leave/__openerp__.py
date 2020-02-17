# -*- coding: utf-8 -*-
{
    'name': 'Coop - Parental Leave',
    'version': '9.0.2.0.0',
    'category': 'Custom',
    'summary': 'Custom settings for Parental Leave',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'coop_shift',
    ],
    'data': [
        # Classical Data
        'views/view_shift_leave.xml',

        # Custom Data
        'data/ir_cron.xml',
        'data/email_template_data.xml',
    ],
    'installable': True,
}
