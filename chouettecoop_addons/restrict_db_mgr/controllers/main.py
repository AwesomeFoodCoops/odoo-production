# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 OpenSur.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import http
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.addons.web.controllers.main import Database
from openerp.exceptions import AccessError
import werkzeug.utils

ADMIN_CATEGORY = 'Administration'
ADMIN_GROUP = 'Access Rights'

class Database_restrict(Database):

    def _is_usr_admin(self):
        uid = request.session.uid
        if uid == SUPERUSER_ID:
            return True
        cr, context, registry = request.cr, request.context, request.registry
        admin_category = registry('ir.module.category').search(
                cr, SUPERUSER_ID, [('name','=',ADMIN_CATEGORY),])
        if len(admin_category):
            admin_group = registry('res.groups').search(cr, SUPERUSER_ID,
                ['&', ('name','=',ADMIN_GROUP),
                      ('category_id','=',admin_category[0]),])
            if len(admin_group):
                user_id = registry('res.groups').search(
                    cr, SUPERUSER_ID,
                    [('id','=',admin_group[0]), ('users','in', [uid])],
                    context=context)
                return user_id and True or False
        return False

    def _access_forbidden(self):
        return werkzeug.utils.redirect('/web/login', 303)

    @http.route('/web/database/manager')
    def manager(self, *args, **kwargs):
        if self._is_usr_admin():
            return super(Database_restrict, self).manager(*args, **kwargs)
        else:
            return self._access_forbidden()

    @http.route('/web/database/create')
    def create(self, *args, **kwargs):
        if self._is_usr_admin():
            return super(Database_restrict, self).create(*args, **kwargs)
        else:
            return self._access_forbidden()

    @http.route('/web/database/duplicate')
    def duplicate(self, *args, **kwargs):
        if self._is_usr_admin():
            return super(Database_restrict, self).duplicate(*args, **kwargs)
        else:
            return self._access_forbidden()

    @http.route('/web/database/drop')
    def drop(self, *args, **kwargs):
        if self._is_usr_admin():
            return super(Database_restrict, self).drop(*args, **kwargs)
        else:
            return self._access_forbidden()

    @http.route('/web/database/backup')
    def backup(self, *args, **kwargs):
        if self._is_usr_admin():
            return super(Database_restrict, self).backup(*args, **kwargs)
        else:
            return self._access_forbidden()

    @http.route('/web/database/restore')
    def restore(self, *args, **kwargs):
        if self._is_usr_admin():
            return super(Database_restrict, self).restore(*args, **kwargs)
        else:
            return self._access_forbidden()

    @http.route('/web/database/change_password')
    def change_password(self, *args, **kwargs):
        if self._is_usr_admin():
            return super(Database_restrict, self).change_password(*args, **kwargs)
        else:
            return self._access_forbidden()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
