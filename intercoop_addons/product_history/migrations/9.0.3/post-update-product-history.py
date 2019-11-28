# -*- coding: utf-8 -*-

from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


def migrate(cr, installed_version):
    registry = RegistryManager.get(cr.dbname)
    history_obj = registry['product.history']
    history_obj.product_history_update_background(cr, SUPERUSER_ID)
