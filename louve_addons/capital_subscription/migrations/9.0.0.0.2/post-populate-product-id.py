# -*- coding: utf-8 -*-

import logging
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

logger = logging.getLogger('openerp.capital_subscription')


def populate_product_id(cr, registry, model):
    cfc_obj = registry['capital.fundraising.category']
    am_obj = registry['account.move']
    aml_obj = registry[model]
    cfc_ids = cfc_obj.search(cr, SUPERUSER_ID, [])
    account_ids = tuple(c.partner_account_id.id for c in cfc_obj.browse(
        cr, SUPERUSER_ID, cfc_ids))
    accounts2 = tuple(c.capital_account_id for c in cfc_obj.browse(
        cr, SUPERUSER_ID, cfc_ids))
    account_ids2 = tuple(c.capital_account_id.id for c in cfc_obj.browse(
        cr, SUPERUSER_ID, cfc_ids))
    move_lines = aml_obj.search(cr, SUPERUSER_ID, [
        ('account_id', 'in', account_ids)])
    move_lines = aml_obj.browse(cr, SUPERUSER_ID, move_lines)
    move_lines2 = aml_obj.search(cr, SUPERUSER_ID, [
        ('account_id', 'in', account_ids2)])
    move_lines2 = aml_obj.browse(cr, SUPERUSER_ID, move_lines2)
    nb_moves = len(move_lines) + len(move_lines2)
    migrated_move_ids = []

    i = 0
    for line in move_lines:
        i += 1
        logger.info(
            "Populating product_id for move_line %s/%s"
            % (i, nb_moves))
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

    product_account = {}
    for account in accounts2:
        category_id = cfc_obj.search(cr, SUPERUSER_ID, [
            ('capital_account_id', '=', account.id)])
        category = cfc_obj.browse(cr, SUPERUSER_ID, category_id)
        product_account[account.id] = category.product_id.id
    for line in move_lines2:
        i += 1
        logger.info(
            "Populating product_id for move_line %s/%s"
            % (i, nb_moves))
        if line.move_id.id in migrated_move_ids:
            continue
        line.product_id = product_account[line.account_id.id]
        move_id = am_obj.search(cr, SUPERUSER_ID, [
            ('name', '=', line.ref)])
        if move_id:
            move = am_obj.browse(cr, SUPERUSER_ID, move_id)
            for l in move.line_ids:
                invoice_id = l.invoice_id
                if invoice_id:
                    break
            line.invoice_id = invoice_id.id
        migrated_move_ids.append(line.move_id.id)


def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)
    populate_product_id(cr, registry, 'account.move.line')
