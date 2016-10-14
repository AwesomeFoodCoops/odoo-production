# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Louve Custom - Date Search',
    'version': '9.0.1.0.0',
    'category': 'Custom',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/view_pos_order.xml',
        'views/view_pos_session.xml',
        'views/view_account_move.xml',
        'views/view_account_move_line.xml',
    ],
    'installable': True,
}
