# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

from openerp.addons.coop_badge_reader.models.res_partner import\
    BADGE_PARTNER_BOOTSTRAP_COOPERATIVE_STATE

from openerp.addons.coop_membership.models.res_partner import\
    EXTRA_COOPERATIVE_STATE_SELECTION


ACTION_SELECTION = [
    ('in', 'In'),
    ('out', 'Out'),
    ('wrong', 'Wrong Partner'),
]


class ResPartnerMove(models.Model):
    _name = 'res.partner.move'
    _order = 'create_date desc, partner_id'

    # Column Section
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner', required=True,
        select=True)

    action = fields.Selection(
        selection=ACTION_SELECTION, string='Action', required=True,
        select=True, default='in')

    cooperative_state = fields.Selection(
        selection=EXTRA_COOPERATIVE_STATE_SELECTION, state='state',
        required=True)

    bootstrap_cooperative_state = fields.Selection(
        selection=BADGE_PARTNER_BOOTSTRAP_COOPERATIVE_STATE,
        state='Boostrap Cooperative State', required=True)
    is_danger = fields.Boolean(string="Danger",
                               related="partner_id.badge_to_distribute",
                               )

    @api.multi
    def set_badge_distributed(self):
        for record in self:
            if record.partner_id:
                record.partner_id.write({
                    'badge_distribution_date': fields.Date.context_today(self)
                })
