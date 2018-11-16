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
        Add users Tom Boothe and Mathilde Virard to
        group Access Res Partner Inform to access res.partner.inform
        """
        # remove normal users from
        # coop_membership.coop_group_access_res_partner_inform
        _logger.info(">>>>> START: Adjust User Right <<<<<<")
        group_acess_res_partner_inform = \
            self.env.ref('coop_membership.coop_group_access_res_partner_inform')
        selected_users = self.env['res.users'].search([
            '|',
            ('login', '=', 'tkboothe@cooplalouve.fr'),
            ('login', '=', 'mathilde.virard@gmail.com'),
        ])
        group_acess_res_partner_inform.write({
            'users': [[6, 0, selected_users.ids]]
        })
        _logger.info(">>>>> END: Adjust User Right <<<<<<")
