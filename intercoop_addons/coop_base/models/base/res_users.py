# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<https://cooplalouve.fr>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models  # @UnresolvedImport
import logging  # @UnresolvedImport
from lxml import etree  # @UnresolvedImport
from openerp.osv.orm import setup_modifiers   # @UnresolvedImport
import openerp   # @UnresolvedImport
_logger = logging.getLogger(__name__)

def name_boolean_group(id):
    return 'in_group_' + str(id)

class ResUsers(models.Model):

    _inherit = "res.users"

    @api.multi
    def _is_admin(self):
        """
        - modify _is_admin function in res.users
        - admin is superuser or has group group_funtional_admin to allow read full res_users
        """
        # only support one object
        self.ensure_one()

        return self.id == openerp.SUPERUSER_ID or\
            self.sudo(self).has_group('coop_base.group_funtional_admin')

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}

        res = super(ResUsers, self).fields_view_get(cr, uid,
                                                    view_id=view_id,
                                                    view_type=view_type,
                                                    context=context,
                                                    toolbar=toolbar,
                                                    submenu=submenu)

        model_data_obj = self.pool['ir.model.data']
        admin_settings_id = model_data_obj.xmlid_to_res_id(
            cr, openerp.SUPERUSER_ID, 'base.group_system')
        admin_settings_fname = name_boolean_group(admin_settings_id)

        admin_access_rights_id = model_data_obj.xmlid_to_res_id(
            cr, openerp.SUPERUSER_ID, 'base.group_erp_manager')
        admin_rights_fname = name_boolean_group(
            admin_access_rights_id
        )

        # Hide some admin rights field to avoid granting these groups to user
        admin_fields = (admin_settings_fname, admin_rights_fname)
        doc = etree.fromstring(res['arch'])
        if view_type == 'form':
            for node in doc.xpath("//field"):
                node_name = node.get('name')
                if node.get('name') in admin_fields:
                    node.set('invisible', '1')
                setup_modifiers(node)
        res['arch'] = etree.tostring(doc)

        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
