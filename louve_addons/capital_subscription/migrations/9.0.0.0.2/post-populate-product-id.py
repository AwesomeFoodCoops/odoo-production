# -*- coding: utf-8 -*-

import logging
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

logger = logging.getLogger('openerp.capital_subscription')


def populate_product_id(cr, registry, model):
    cfc_obj = registry['capital.fundraising.category']
    cfc_ids = cfc_obj.search(cr, SUPERUSER_ID, [])
    account_ids = tuple(c.partner_account_id.id for c in cfc_obj.browse(
        cr, SUPERUSER_ID, cfc_ids))
    aml_obj = registry[model]
    move_lines = aml_obj.search(cr, SUPERUSER_ID, [
        ('account_id', 'in', account_ids)])
    move_lines = aml_obj.browse(cr, SUPERUSER_ID, move_lines)
    migrated_move_ids = []
    i = 0
    for line in move_lines:
        i += 1
        logger.info(
            "Populating product_id for move_line %s/%s"
            % (i, len(move_lines)))
        if line.move_id.id in migrated_move_ids:
            continue
        lines = line.move_id.line_ids
        for l in lines:
            product_id = l.product_id
            if product_id:
                break
        for l in lines:
            if not l.product_id:
                l.product_id = product_id
        migrated_move_ids.append(line.move_id.id)


def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)
    populate_product_id(cr, registry, 'account.move.line')
