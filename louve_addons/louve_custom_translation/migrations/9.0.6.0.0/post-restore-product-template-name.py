# -*- coding: utf-8 -*-

import logging
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

logger = logging.getLogger('openerp.louve_change_translation')
_COUNTER_DISPLAY = 50


def disable_translation(cr, registry, model, field_name):
    cr.execute("""
        SELECT res_id,value
        FROM ir_translation
        WHERE name='%s,%s'
        AND type='model'
    """ % (model, field_name))
    translations = cr.fetchall()
    logger.info(
        "Disabling translation for the field '%s' (model '%s'), "
        "%d items found." % (field_name, model, len(translations)))
    model_obj = registry[model]
    i = 0
    for translation in translations:
        i += 1
        model_obj.write(
            cr, SUPERUSER_ID, [translation[0]],
            {field_name: translation[1]})
        if i % _COUNTER_DISPLAY == 0 or i == len(translations):
            logger.info(
                "translations disabled : %d / %d." % (i, len(translations)))
    cr.execute("""
        DELETE
        FROM ir_translation
        WHERE name='%s,%s'
        AND type='model'
    """ % (model, field_name))


def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)
    disable_translation(cr, registry, 'product.template', 'name')
