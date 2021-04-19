# -*- coding: utf-8 -*-
from openerp import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

def update_translation(env, xmlIDs, name, lang, module, ttype, source, tovalue):
    res_ids = []
    for xmlID in xmlIDs:
        if env.ref(xmlID, False):
            res_ids.append(env.ref(xmlID).id)
    if res_ids:
        args = [
            ('name', '=', name),
            ('lang', '=', lang),
            ('module', '=', module),
            ('type', '=', ttype),
            ('res_id', 'in', res_ids),
            ('source', '=', source)
        ]
        terms = env['ir.translation'].search(args)
        if terms:
            terms.write({'value': tovalue})

def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _logger.info(
            'Update the translation')
        update_translation(
            env,
            ['account.account_account_menu', 'account.menu_finance'],
            'ir.ui.menu,name',
            'fr_FR',
            'account',
            'model',
            'Accounting',
            'Facturation'
        )
        update_translation(
            env,
            ['coop_shift.field_shift_shift_shift_template_id'],
            'ir.model.fields,field_description',
            'fr_FR',
            'coop_shift',
            'model',
            'Template',
            'Créneau'
        )
        update_translation(
            env,
            ['coop_shift.field_res_partner_cooperative_state'],
            'ir.model.fields,field_description',
            'fr_FR',
            'coop_shift',
            'model',
            'Cooperative State',
            'Statut'
        )
