# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    related_user_id = fields.Many2one('res.users',
                                      compute="_compute_related_user",
                                      string="Related User")

    @api.multi
    def _compute_related_user(self):
        '''
        Function to compute the related user of the partner
        '''
        res_user_env = self.env["res.users"]
        for partner in self:
            related_users = res_user_env.search(
                [('partner_id', '=', partner.id)])
            partner.related_user_id = \
                related_users and related_users[0] or False

    @api.multi
    def action_create_new_user(self):
        '''
        Function to activate the User Creation Form
        '''
        self.ensure_one()

        # Prepare context for default value
        context = self.env.context.copy()
        context.update({
            'default_partner_id': self.id,
            'default_name': self.name,
            'default_login': self.email,
            'default_email': self.email
        })

        return {
            'name': _('Create New User'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'res.users',
            'views': [(self.env.ref("base.view_users_form").id, 'form')],
            'type': 'ir.actions.act_window',
        }
