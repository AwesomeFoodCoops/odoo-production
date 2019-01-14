# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Coop Badge Reader',
    'version': '9.0.0.0.0',
    'category': 'Custom',
    'summary': 'Provide light Ionic Apps to read user Badge',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
        'coop_shift',
        'coop_membership',
    ],
    'data': [
        'data/mail_template.xml',
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/view_res_partner.xml',
        'views/view_res_partner_alert.xml',
        'views/view_res_partner_move.xml',
        'views/view_shift_extension_type.xml',
        'views/view_shift_extension.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/res_users.xml',
        'demo/res_partner.xml',
    ],
    'installable': True,
}
