# -*- coding: utf-8 -*-
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model


class product_scale_group(Model):
    _name = 'product.scale.group'

    # Compute Section
    def _compute_product_qty(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for group in self.browse(cr, uid, ids, context):
            res[group.id] = len(group.product_ids)
        return res

    # Column Section
    _columns = {
        'name': fields.char(
            string='Name', required=True),
        'active': fields.boolean(
            string='Active'),
        'external_identity': fields.char(
            string='External ID', required=True),
        'company_id': fields.many2one(
            'res.company', string='Company', select=True),
        'scale_system_id': fields.many2one(
            'product.scale.system', string='Scale System', required=True),
        'product_ids': fields.one2many(
            'product.product', 'scale_group_id', 'Products'),
        'product_qty': fields.function(
            _compute_product_qty, type='integer', string='Products Quantity'),
    }

    _defaults = {
        'active': True,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company').
        _company_default_get(cr, uid, 'product.product', context=c),
    }
