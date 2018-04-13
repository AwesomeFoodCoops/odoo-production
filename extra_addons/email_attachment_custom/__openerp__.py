# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Email Attachment Custom',
    'version': '9.0.7.0.0',
    'category': 'Email',
    'description': '''
        Allow to add attachments to email template with condition.
    ''',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        # VIEWS
        "view/view_mail_attachment_custom.xml",
        "view/view_mail_template.xml",

        # SECURITY
        "security/ir_model_access.yml",
    ],
    'demo': [],
}
