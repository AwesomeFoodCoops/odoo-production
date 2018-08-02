# -*- coding: utf-8 -*-

import openerp
from openerp.addons.web import http
from openerp.http import request


class DataSet(openerp.addons.web.controllers.main.DataSet):
    def _call_kw(self, model, method, args, kwargs):
        if 'context' in kwargs and \
            kwargs['context'].get('member_space', False):
            member_space_user_id =\
                int(request.env['ir.config_parameter'].sudo(
                ).get_param('member_space_user'))
            return getattr(request.registry.get(model),
                method)(request.cr, member_space_user_id, *args, **kwargs)
        return super(DataSet, self)._call_kw(model, method, args, kwargs)
