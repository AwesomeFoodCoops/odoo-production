# -*- coding: utf-8 -*-

from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


def migrate(cr, installed_version):
    registry = RegistryManager.get(cr.dbname)
    module_obj = registry['ir.module.module']
    module_ids = module_obj.search(
        cr, SUPERUSER_ID, [('name', '=', 'l10n_fr_fec_custom'),
                           ('state', '=', 'uninstalled')])
    module_obj.button_install(cr, SUPERUSER_ID, module_ids, {})
