# -*- coding: utf-8 -*-

from openerp import models, api, fields
from openerp.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_warning_member_state(self):
        IrConfig  = self.env['ir.config_parameter']
        warning_member_state = safe_eval(IrConfig.sudo().get_param(
            'warning_member_state'))
        if not (self.cooperative_state and warning_member_state.has_key(
            self.cooperative_state)):
            return warning_member_state['none']['alert'] + ' ' + \
                warning_member_state['none']['message']
        return warning_member_state[self.cooperative_state]['alert'] + ' ' + \
            warning_member_state[self.cooperative_state]['message']

    public_avatar = fields.Boolean(
        "Public Avatar", help="Public your avatar in website")
    public_mobile = fields.Boolean(
        "Public Mobile", help="Public your mobile in website")
    public_email = fields.Boolean(
        "Public Email Address", help="Public your email address on website"
    )

    @api.multi
    def create_memberspace_user(self):
        members_dont_have_user = self.filtered(lambda r: not r.related_user_id)
        # portal group
        portal_group = self.env.ref('base.group_portal')
        # memberspace group
        memberspace_group = self.env.ref(
            'foodcoop_memberspace.group_memberspace')
        Users = self.env['res.users']
        context = self.env.context.copy()
        context.update({
            'default_groups_id': [
                (6, 0, [portal_group.id, memberspace_group.id])]
        })
        vals = Users.with_context(context).default_get(Users._fields.keys())
        for member in members_dont_have_user:
            sql = '''
                SELECT id
                FROM res_users
                WHERE login = '%s'
                LIMIT 1
            ''' % (member.email)
            self.env.cr.execute(sql)
            user = self.env.cr.fetchone()
            if user:
                user = Users.browse(user[0])
            if not user:
                vals.update({
                    'partner_id': member.id,
                    'name': member.name,
                    'login': member.email,
                    'email': member.email
                })
                # Users.with_context(no_reset_password=True).create(vals)
                Users.create(vals)
            elif user.active:
                user.partner_id = member.id
        return True
