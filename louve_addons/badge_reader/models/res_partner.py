# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

# TODO @LA LOUVE. Set exhaustive state
_BADGE_PARTNER_STATE = [
    ('ok', 'OK'),
    ('membership_problem', 'Membership Problem'),
    ('work_problem', 'Work Problem'),
]

_BADGE_PARTNER_BOOTSTRAP_STATE = [
    ('success', 'OK'),
    ('warning', 'Warning'),
    ('danger', 'Danger'),
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Column Section
    state = fields.Selection(
        selection=_BADGE_PARTNER_STATE, state='state', default='ok')

    bootstrap_state = fields.Selection(
        compute='_compute_bootstrap_state', string='Bootstrap State',
        selection=_BADGE_PARTNER_BOOTSTRAP_STATE, store=True)

    # Compute Section
    @api.multi
    @api.depends('state')
    def _compute_bootstrap_state(self):
        for partner in self:
            # TODO @LA LOUVE. Define boostrap state for each partner state
            if partner.state == 'work_problem':
                partner.bootstrap_state = 'danger'
            elif partner.state == 'membership_problem':
                partner.bootstrap_state = 'warning'
            elif partner.state == 'ok':
                partner.bootstrap_state = 'success'
