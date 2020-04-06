# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval


class UsersConfigSettings(models.TransientModel):
    _name = 'user.config.settings'
    _inherit = 'res.config.settings'

    configuration_user_ids = fields.Many2many(
        comodel_name='res.users'
    )

    @api.model
    def default_get(self, fields_list):
        res = super(UsersConfigSettings, self).default_get(fields_list)
        if 'configuration_user_ids' in fields_list:
            configuration_user_ids = \
                self.env.user.company_id.configuration_user_ids
            if configuration_user_ids:
                res.update({
                    'configuration_user_ids': [
                        [6, 0, configuration_user_ids.ids]
                    ]
                })
        return res

    @api.multi
    def execute(self):
        for record in self:
            self.env.user.company_id.write({
                'configuration_user_ids': [
                    [6, False, record.configuration_user_ids.ids]
                ]
            })

        return super(UsersConfigSettings, self).execute()
