# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp import SUPERUSER_ID


class ResCompany(models.Model):
    _inherit = "res.company"

    configuration_user_ids = fields.Many2many(
        comodel_name='res.users'
    )

    @api.multi
    def write(self, vals):
        res = super(ResCompany, self).write(vals)
        if 'configuration_user_ids' in vals:
            # Add configuration_user_ids
            # to group admin settings and group functional admin
            group_admin_settings = self.env.ref('base.group_system')
            group_erp_manager = self.env.ref('base.group_erp_manager')
            group_configuration = self.env.ref('base.group_configuration')
            group_functional_admin = \
                self.env.ref('coop_base.group_funtional_admin')
            configuration_user_ids = vals['configuration_user_ids']
            configuration_user_ids[0][2].append(SUPERUSER_ID)
            user_vals = {
                'users': configuration_user_ids
            }
            root_user_vals = {
                'users': [[6, 0, [SUPERUSER_ID]]]
            }
            group_admin_settings.write(user_vals)
            group_functional_admin.write(user_vals)
            group_erp_manager.write(root_user_vals)
            group_configuration.write(root_user_vals)
        return res
