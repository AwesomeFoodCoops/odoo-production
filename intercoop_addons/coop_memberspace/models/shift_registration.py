# -*- coding: utf-8 -*-

from openerp import models, api


class ShiftRegistration(models.Model):
    _inherit = 'shift.registration'

    @api.model
    def get_coordinators(
        self, shift_regis_id=None, get_alias_coordinator=False):
        # Function return name of the coordinators with format:
        #   A, B, C, D

        # @param shift_id: Use to call function in js.
        shift = shift_regis_id and self.browse(shift_regis_id) and \
            self.browse(shift_regis_id).shift_id or self.shift_id
        coordinators = shift.user_ids and \
            shift.user_ids.mapped("name") or []
        
        # Get alias coordinator
        alias_coordinator = self.env['memberspace.alias'].search([
            ('shift_id', '=', shift.id),
            ('type', '=', 'coordinator')
        ], limit=1)
        alias_coordinator = alias_coordinator.alias_id.name_get()[0][1] \
            if alias_coordinator else ''
        coordinators = ", ".join(coordinators) if coordinators else ""
        if get_alias_coordinator:
            return coordinators, alias_coordinator
        return coordinators

    @api.model
    def create(self, vals):
        res = super(ShiftRegistration, self).create(vals)

        # Add follower to memberspace alias
        memberspace_alias = self.env['memberspace.alias'].search(
            [('shift_id', '=', res.shift_id.id), ('type', '=', 'team')],
            limit=1
        )
        if memberspace_alias and \
                res.state in ('draft', 'open', 'done', 'replacing'):
            memberspace_alias.message_subscribe(
                partner_ids=[res.partner_id.id])
        return res
