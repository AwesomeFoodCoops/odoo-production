# -*- coding: utf-8 -*-

from openerp import models, api, fields


class ShiftTemplate(models.Model):
    _inherit = 'shift.template'

    memberspace_alias_ids = fields.One2many(
        'memberspace.alias', 'shift_id', "Memberspace Alias")

    @api.model
    def create(self, vals):
        res = super(ShiftTemplate, self).create(vals)
        # generate automatically an alias
        res.create_email_alias()
        return res

    @api.multi
    def create_email_alias(self):
        self.ensure_one()
        name = self.name + (self.start_datetime and
            (' ' + self.start_datetime) or '')
        alias_prefix = "_".join(
            name.replace('-', '').replace('.', '').split(' '))
            # 1. for the coordinators of the team
        self.env['memberspace.alias'].create({
            'name': name + ' - Leader',
            'shift_id': self.id,
            'alias_name': '%s_leader' % (alias_prefix),
            'type': 'coordinator'
        })
            # 2. for the members of the team (include coordinators))
        self.env['memberspace.alias'].create({
            'name': name + ' - Team',
            'shift_id': self.id,
            'alias_name': '%s_team' % (alias_prefix),
            'type': 'team'
        })

    @api.multi
    def generate_email_alias(self):
        records = self.filtered(lambda r: len(r.memberspace_alias_ids) < 1)
        for record in records:
            record.create_email_alias()