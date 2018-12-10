# -*- coding: utf-8 -*-
from openerp import api, models
from openerp import SUPERUSER_ID


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.multi
    def write(self, vals):
        res = super(ResCompany, self).write(vals)
        if 'configuration_user_ids' in vals:
            # Add configuration_user_ids
            # to group admin settings and group functional admin
            group_admin_settings = self.env.ref('base.group_system')
            group_functional_admin = \
                self.env.ref('l10n_fr_pos_cert_base.group_funtional_admin')
            configuration_user_ids = vals['configuration_user_ids']
            configuration_user_ids[0][2].append(SUPERUSER_ID)
            user_vals = {
                'users': configuration_user_ids
            }
            group_admin_settings.write(user_vals)
            group_functional_admin.write(user_vals)
        return res
