# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, fields


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    @api.multi
    def open_entries(self):
        res = super(AccountAssetAsset, self).open_entries()
        res.update({
            'domain': [('asset_id', '=', self.id)],
        })
        return res
