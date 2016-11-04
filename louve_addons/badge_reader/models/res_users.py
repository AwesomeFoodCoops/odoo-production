# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    # TODO Improve Odoo-JS lib
    # Exist because 'has_group' function doesn't accept context args
    # that is not manage by the Odoo-JS lib
    def check_group(self, cr, uid, group_ext_id, context=None):
        return self.has_group(cr, uid, group_ext_id)
