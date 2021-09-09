# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Coop Memberspace',
    'description': """
        Version 0.0.0.3 : inscription à un service (volant ou rattrapage) possible depuis la page planning
        Version 0.0.0.2 : ajout de la page planning par Supercoop pour visualiser les prochains services confirmés avec le nombre de places disponibles 
    """,
    'version': '0.0.0.3',
    'category': 'Custom',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'website',
        'coop_shift',
        'theme_bootswatch',
        'email_pos_receipt',
        'create_users_partners'
    ],
    'data': [
        'security/res_group_data.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',

        'data/email/memberspace_alias_send_error_email.xml',
        'data/email/email_proposal.xml',
        'data/change_name_menu_homepage.yml',
        'data/deactive_ir_rule.yml',
        'data/generate_email_alias_for_shift_template.yml',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'data/website_menu.xml',

        'views/res_partner_view.xml',
        'views/memberspace_alias_view.xml',
        'views/memberspace_conversation_view.xml',
        'views/templates.xml',
        'views/view_pos_config_settings.xml',

        'views/website/proposal_confirm.xml',
        'views/website/my_work.xml',
        'views/website/my_team.xml',
        'views/website/my_profile.xml',
        'views/website/my_documents.xml',
        'views/website/statistics.xml',
        'views/website/website_homepage.xml',
        'views/website/website_template.xml',
        'views/website/planning.xml',
    ],
    'installable': True,
}
