# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):

        # Identify if deprecated element exists in the args or not
        key_elements = [arg_item[0] for arg_item in args]

        if not self._context.get('search_all_accounts', False):
            if 'deprecated' not in key_elements:
                # If deprecated element is not found, only include
                # not-deprecated account in the search result.
                args.append(('deprecated', '=', False))

        return super(AccountAccount, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count)
