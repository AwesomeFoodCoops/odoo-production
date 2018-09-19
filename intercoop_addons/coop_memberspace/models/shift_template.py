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
        template_name = self.name.replace(' ', '').split('-')
        if self.shift_type_id.is_ftop and len(template_name) > 2:
            prefix = "%s%s" % (template_name[1][:3], template_name[2][:2])
        else:
            prefix = "%s%s" % (template_name[0][:3], template_name[1][:2])

            # 1. for the coordinators of the team
        leader_alias_prefix = 'coordos.%s' % (prefix)
        self.env['memberspace.alias'].create({
            'name': leader_alias_prefix,
            'shift_id': self.id,
            'alias_name': leader_alias_prefix,
            'type': 'coordinator'
        })
            # 2. for the members of the team (include coordinators))
        team_alias_prefix = 'service.%s' % (prefix)
        self.env['memberspace.alias'].create({
            'name': team_alias_prefix,
            'shift_id': self.id,
            'alias_name': team_alias_prefix,
            'type': 'team'
        })

    @api.multi
    def generate_email_alias(self):
        records = self.filtered(lambda r: len(r.memberspace_alias_ids) < 1)
        for record in records:
            record.create_email_alias()