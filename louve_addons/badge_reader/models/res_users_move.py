# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

from openerp.addons.badge_reader.models.res_partner import (
    _BADGE_PARTNER_BOOTSTRAP_STATE,
    _BADGE_PARTNER_STATE,
)


class ResUsersMove(models.Model):
    _name = 'res.users.move'
    _order = 'create_date desc, user_id'

    # Column Section
    user_id = fields.Many2one(
        comodel_name='res.users', string='User', required=True, select=True)

    bootstrap_state = fields.Selection(
        selection=_BADGE_PARTNER_BOOTSTRAP_STATE, state='Boostrap State',
        required=True)

    state = fields.Selection(
        selection=_BADGE_PARTNER_STATE, state='state',
        required=True)
