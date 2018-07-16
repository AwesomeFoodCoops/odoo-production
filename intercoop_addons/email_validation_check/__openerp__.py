# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Email Validation Check',
    'version': '9.0.1.0.11',
    'category': 'Custom',
    'description': """
        Validation email for Partner
    """,

    'license': 'AGPL-3',
    'depends': [
        'coop_membership',
    ],
    'data': [
        'data/email_template_data.xml',
        'views/view_res_partner.xml',
        'views/template_confirm.xml',
    ],
}
