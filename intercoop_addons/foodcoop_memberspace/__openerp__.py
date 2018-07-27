# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'FoodCoop Memberspace',
    'version': '0.0.0.1',
    'category': 'Custom',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'website'
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'data/website_menu.xml',
        'views/templates.xml',
        'views/website/my_work.xml',
        'views/website/my_team.xml',
        'views/website/website_homepage.xml',
        'views/website/website_template.xml',
    ],
    'installable': True,
}
