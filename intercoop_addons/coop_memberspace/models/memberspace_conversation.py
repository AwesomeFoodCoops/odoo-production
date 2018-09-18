# -*- coding: utf-8 -*-

from openerp import models, fields, api


class MemberSpaceConversation(models.Model):
    _name = 'memberspace.conversation'
    _inherit = ['mail.thread']

    name = fields.Char("Name", required=True)
    memberspace_alias_id = fields.Many2one(
        "memberspace.alias", "Shift Alias", required=True)

    @api.model
    def create(self, vals):
        res = super(MemberSpaceConversation, self).create(vals)
        alias = res.memberspace_alias_id
        partners = alias.shift_id.user_ids
        if alias.type == 'team':
            partners |= alias.shift_id.registration_ids.filtered(
                lambda r: r.is_current_participant).mapped('partner_id')
        res.message_subscribe(partner_ids=partners.ids)
        return res
