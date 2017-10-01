# coding: utf-8
# Copyright 2014 Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
import base64


class ProxyActionHelper(models.AbstractModel):
    _name = "proxy.action.helper"
    _description = "Forward HTTP call to front-end proxy"
    
    def send_proxy(self, url):
            """ @param url: local url to call
            """
            return {
                'type': 'ir.actions.act_proxy',
                'url': url,
    }
