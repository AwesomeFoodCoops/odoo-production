# -*- coding: utf-8 -*-

from openerp import api, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        args.append(('deprecated', '=', False))
        return super(AccountAccount, self).name_search(
            name, args, operator, limit)

