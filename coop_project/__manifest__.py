# -*- coding: utf-8 -*-
{
    'name': 'Coop - Project',
    'version': '12.0.1.0.0',
    'category': 'Custom',
    'description': """
Lalouve Custom    """,
    'author': 'Trobz',
    'website': 'http://www.trobz.com',
    'depends': [
        'calendar',
        'project',
    ],
    'data': [
        'data/project_data.xml',
        'data/mail_template.xml',
        'security/ir.model.access.csv',
        'view/calendar_view.xml',
        "view/mail_message_view.xml",
        "view/project_view.xml",
        "view/project_category_view.xml",
        'view/assets.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'test': [],
    'installable': True,
}
