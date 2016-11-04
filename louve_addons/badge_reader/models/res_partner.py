# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

BADGE_PARTNER_BOOTSTRAP_COOPERATIVE_STATE = [
    ('success', 'OK'),
    ('warning', 'Warning'),
    ('danger', 'Danger'),
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    MAPPING_COOPERATIVE_STATE = {
        'up_to_date': 'success',
        'alert': 'warning',
        'delay': 'warning',
        'suspended': 'danger',
        'not_concerned': 'danger',
        'blocked': 'danger',
        'unpayed': 'danger',
        'unsubscribed': 'danger',
    }

    bootstrap_cooperative_state = fields.Selection(
        compute='_compute_bootstrap_cooperative_state',
        string='Bootstrap State', store=True,
        selection=BADGE_PARTNER_BOOTSTRAP_COOPERATIVE_STATE)

    # Compute Section
    @api.depends('cooperative_state')
    @api.multi
    def _compute_bootstrap_cooperative_state(self):
        for partner in self:
            partner.bootstrap_cooperative_state =\
                self.MAPPING_COOPERATIVE_STATE.get(
                    partner.cooperative_state, 'danger')

    # Custom Section
    @api.multi
    def log_move(self):
        partner_move_obj = self.env['res.partner.move']
        for partner in self:
            partner_move_obj.create({
                'partner_id': partner.id,
                'cooperative_state': partner.cooperative_state,
                'bootstrap_cooperative_state':
                partner.bootstrap_cooperative_state,
            })
