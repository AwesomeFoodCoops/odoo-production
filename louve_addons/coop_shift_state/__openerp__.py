# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Cyril Gaspard
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Julien WESTE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Coop Shift state',
    'version': '1.0',
    'category': 'Tools',
    'description': """
This module add state to partners depending of its attendees
    """,
    'author': 'Cyril Gaspard,'
              'Julien Weste,'
              'La Louve',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'coop_shift',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/shift_security.xml',
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'data/ir_config_parameter.xml',
        'views/action.xml',
        'views/view_shift_extension.xml',
        'views/view_res_partner.xml',
        'views/view_shift_extension_type.xml',
        'views/report_timesheet.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
    ],
}
