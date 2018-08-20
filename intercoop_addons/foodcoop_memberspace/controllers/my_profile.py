# -*- coding: utf-8 -*-

import openerp
from openerp.addons.web import http
from openerp.http import request
from openerp import tools
from datetime import datetime
import pytz
import locale


class Website(openerp.addons.website.controllers.main.Website):

    @http.route('/edit-phone', type='http', auth="user", website=True, 
        methods=['POST'])
    def edit_phone(self, **kw):
        request.env.user.partner_id.write(kw)
        return http.local_redirect('/profile')

    @http.route('/edit-address', type='http', auth="user", website=True, 
        methods=['POST'])
    def edit_address(self, **kw):
        request.env.user.partner_id.write(kw)
        return http.local_redirect('/profile')
