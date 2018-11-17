# -*- coding: utf-8 -*-
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class product_template(Model):
    _inherit = 'product.template'

    def write(self, cr, uid, ids, vals, context=None):
        product_obj = self.pool['product.product']
        context = context and context or {}
        ctx = context.copy()
        defered = {}
        if not context.get('bizerba_off', False):
            for template in self.browse(cr, uid, ids, context=context):
                for product in template.product_variant_ids:
                    ignore = not product.scale_group_id\
                        and 'scale_group_id' not in vals.keys()
                    if not ignore:
                        if not product.scale_group_id:
                            # (the product is new on this group)
                            defered[product.id] = 'create'
                        else:
                            if vals.get('scale_group_id', False) and (
                                    vals.get('scale_group_id', False) !=
                                    product.scale_group_id):
                                # (the product has moved from a group to another)
                                # Remove from obsolete group
                                product_obj._send_to_scale_bizerba(
                                    cr, uid, 'unlink', product, context=context)
                                # Create in the new group
                                defered[product.id] = 'create'
                            elif product_obj._check_vals_scale_bizerba(
                                    cr, uid, vals, product, context=context):
                                # Data related to the scale
                                defered[product.id] = 'write'
        ctx['bizerba_off'] = True
        res = super(product_template, self).write(
            cr, uid, ids, vals, context=ctx)

        for product_id, action in defered.iteritems():
            product = product_obj.browse(cr, uid, product_id, context=context)
            product_obj._send_to_scale_bizerba(
                cr, uid, action, product, context=context)

        return res
