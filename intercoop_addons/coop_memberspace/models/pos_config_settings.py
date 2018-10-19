# -*- coding: utf-8 -*-

from lxml import etree
from openerp import models, api
from openerp.osv.orm import setup_modifiers


class PosConfigSettings(models.Model):
    _inherit = 'pos.config.settings'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(PosConfigSettings, self).fields_view_get(
            view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='receipt_options']")
            user = self.env.user
            has_group_memberspace = user.has_group(
                'coop_memberspace.group_memberspace')
            if nodes:
                if not has_group_memberspace or (
                        has_group_memberspace and not user.active):
                    nodes[0].set('invisible', '1')
                    setup_modifiers(nodes[0], res['fields']['receipt_options'])
                    res['arch'] = etree.tostring(doc)
        return res
