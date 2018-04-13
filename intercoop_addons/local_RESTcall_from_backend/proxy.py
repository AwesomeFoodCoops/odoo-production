# coding: utf-8
# Copyright 2014 Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
import base64


class ProxyActionHelper(models.AbstractModel):
    _name = "proxy.action.helper"
    _description = "Forward HTTP call to front-end proxy"
    
    def send_proxy(self, request_list):
            """ @param request_list: list of requests to execute => [{'url':'example.com','params':{'p1':'param1','p2':'param2'}}]
            """
            return {
                'type': 'ir.actions.act_proxy',
                'request_list': request_list,
            }
