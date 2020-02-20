# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Coop Badge Reader",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "summary": "Provide light Ionic Apps to read user Badge",
    "author": "La Louve, Druidoo",
    "website": "http://www.lalouve.net",
    "license": "AGPL-3",
    "depends": ["base", "coop_shift", "coop_membership"],
    "data": [
        "data/mail_template.xml",
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/view_res_partner.xml",
        "views/view_res_partner_alert.xml",
        "views/view_res_partner_move.xml",
        "views/view_shift_extension_type.xml",
        "views/view_shift_extension.xml",
        "views/action.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/res_groups.xml",
        "demo/res_users.xml",
        "demo/res_partner.xml",
    ],
    "installable": True,
}
