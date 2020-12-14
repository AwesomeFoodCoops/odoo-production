# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Coop Memberspace",
    "version": "12.0.1.1.3",
    "category": "Custom",
    "author": "La Louve, Druidoo",
    "website": "http://www.lalouve.net",
    "license": "AGPL-3",
    "depends": [
        "website",
        "coop_shift",
        "coop_membership",
        "pos_ticket_send_by_mail",
    ],
    "data": [
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/email/memberspace_alias_send_error_email.xml",
        "data/email/email_proposal.xml",
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "data/website_menu.xml",
        "views/res_partner_view.xml",
        "views/memberspace_alias_view.xml",
        "views/memberspace_conversation_view.xml",
        "views/assets.xml",
        "views/view_pos_config_settings.xml",
        "views/website_views.xml",
        "views/website/proposal_confirm.xml",
        "views/website/my_work.xml",
        "views/website/my_team.xml",
        "views/website/my_profile.xml",
        "views/website/my_documents.xml",
        "views/website/statistics.xml",
        "views/website/website_homepage.xml",
        "views/website/website_template.xml",
    ],
    "installable": True,
}
