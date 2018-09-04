# -*- coding: utf-8 -*-

import openerp
from openerp.addons.web import http
from openerp.http import request
from openerp import tools
from datetime import datetime
import pytz
import locale

UPDATE_PHONE = [
    'mobile', 'phone'
]

UPDATE_ADDRESS = [
    'street', 'city', 'zip'
]

class Website(openerp.addons.website.controllers.main.Website):

    @http.route('/edit-phone', type='http', auth="user", website=True, 
        methods=['POST'])
    def edit_phone(self, **kw):
        new_value = {}
        for field in list(x for x in UPDATE_PHONE if x in kw):
            new_value.update({field: kw.get(field, False)})
        request.env.user.partner_id.write(new_value)
        return http.local_redirect('/profile')

    @http.route('/edit-address', type='http', auth="user", website=True, 
        methods=['POST'])
    def edit_address(self, **kw):
        new_value = {}
        for field in list(x for x in UPDATE_ADDRESS if x in kw):
            new_value.update({field: kw.get(field, False)})
        request.env.user.partner_id.write(new_value)
        return http.local_redirect('/profile')
