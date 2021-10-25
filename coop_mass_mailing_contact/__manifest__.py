# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Mass Mailing - Contact',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'summary': "Create the contact for each member",
    'author': 'Trobz',
    'website': 'https://www.trobz.com',
    'depends': [
        'coop_membership',
    ],
    'data': [
        "data/ir_cron.xml",
        "views/view_mail_mass_mailing.xml",
    ],
    'license': 'AGPL-3',
    'installable': True,
}
