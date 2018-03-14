# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<https://cooplalouve.fr>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, models  # @UnresolvedImport
import logging  # @UnresolvedImport
import openerp   # @UnresolvedImport
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)


class ResUsers(models.TransientModel):
    """
    Run some function to modify data by function tag
    """

    _name = "post.object"

    @api.model
    def adjust_user_rights(self):
        """
        Remove configuration access right of normal users
        and set these users as functional
        """
        # remove normal users from base.group_system
        _logger.info(">>>>> START: Adjust User Right <<<<<<")
        group_admin_settings = self.env.ref('base.group_system')
        # to update user ids
        settings_user_ids = []
        access_right_ids = []
        # only run if there are some user normal user
        if len(group_admin_settings.users) > 1:
            # get current users to switch to functional admin
            settings_user_ids = group_admin_settings.users.ids
            group_admin_settings.write({'users': [[6, 0, [SUPERUSER_ID]]]})

        # remove normal users from base.group_erp_manager
        group_admin_access_rights = self.env.ref('base.group_erp_manager')
        # only run if there are some user normal user
        if len(group_admin_access_rights.users) > 1:
            # get current users to switch to functional admin
            access_right_ids = group_admin_access_rights.users.ids
            group_admin_access_rights.write({'users': [[6, 0, [SUPERUSER_ID]]]})

        if settings_user_ids or access_right_ids:
            functional_admin = self.env.ref('coop_base.group_funtional_admin')
            update_user_ids = [SUPERUSER_ID] + \
                settings_user_ids + access_right_ids
            functional_admin.write({
                'users': [[6, 0, update_user_ids]]
            })
        _logger.info(">>>>> END: Adjust User Right <<<<<<")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
