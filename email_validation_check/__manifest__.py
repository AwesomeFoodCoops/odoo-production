# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Email Validation Check',
    'version': '12.0.1.0.0',
    'category': 'Custom',
    'description': """
        Validation email for Partner
    """,
    'author': 'La Louve, Druidoo',
    'website': 'http://www.lalouve.net',
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
