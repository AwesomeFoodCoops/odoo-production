# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'POS Receipt By Email',
    'version': '9.0.1.0.11',
    'category': 'Custom',
    'description': """
        Send Receipt By Email
    """,

    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        # datas
        'data/email_template_data.xml',
        'data/ir_cron_data.xml',

        # view
        'views/view_pos_config.xml',

        # templates
        'static/src/xml/templates.xml',
    ],
}
