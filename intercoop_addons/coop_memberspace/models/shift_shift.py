# -*- coding: utf-8 -*-

from openerp import models, api


class ShiftShift(models.Model):
    _inherit = 'shift.shift'

    @api.model
    def create(self, vals):
        res = super(ShiftShift, self).create(vals)
        # generate automatically an alias
        name = res.name + (res.begin_date_string and
            (' ' + res.begin_date_string) or '')
        alias_prefix = "_".join(
            name.replace('-', '').replace('.', '').split(' '))
                # 1. for the coordinators of the team
        memberspace_alias_leader = self.env['memberspace.alias'].create({
            'name': name + ' - Leader',
            'shift_id': res.id,
            'alias_name': '%s_leader' % (alias_prefix),
            'type': 'coordinator'
        })
        memberspace_alias_leader.message_subscribe(
            partner_ids=res.user_ids.ids)
                # 2. for the members of the team (include coordinators))
                # Set followers when create shift.registration.
        self.env['memberspace.alias'].create({
            'name': name + ' - Team',
            'shift_id': res.id,
            'alias_name': '%s_team' % (alias_prefix),
            'type': 'team'
        })
        return res
