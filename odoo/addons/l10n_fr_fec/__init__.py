# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2013-2015 Akretion (http://www.akretion.com)

import wizard

from openerp import SUPERUSER_ID


def _auto_install_fr_fec_custom(cr, registry):
    module_obj = registry['ir.module.module']
    module_ids = module_obj.search(
        cr, SUPERUSER_ID, [('name', '=', 'l10n_fr_fec_custom'),
                           ('state', '=', 'uninstalled')])
    module_obj.button_install(cr, SUPERUSER_ID, module_ids, {})
