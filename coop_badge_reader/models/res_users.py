# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    # TODO Improve Odoo-JS lib
    # Exist because 'has_group' function doesn't accept context args
    # that is not manage by the Odoo-JS lib
    @api.model
    def check_groups(self, group):
        return self.has_group(group)
