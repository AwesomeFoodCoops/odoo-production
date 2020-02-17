# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Mass Mailing - Access Right',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'summary': "Limit mass sending to new 'Mass Mailing Manager' group member",
    'author': 'La Louve, Druidoo',
    'website': 'http://www.lalouve.net',
    'depends': [
        'mass_mailing',
    ],
    'data': [
        "security/res_groups.xml",
        "views/view_mail_mass_mailing.xml",
    ],
    'license': 'AGPL-3',
    'demo': [
        "demo/res_groups.xml",
    ],
    'installable': True,
}
