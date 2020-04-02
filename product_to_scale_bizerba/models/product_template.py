# Copyright (C) 2014 GRAP (http://www.grap.coop)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def write(self, vals):
        product_obj = self.env['product.product']
        context = self.env.context
        ctx = context.copy()
        defered = {}
        if not context.get('bizerba_off', False):
            for template in self:
                for product in template.product_variant_ids:
                    ignore = not product.scale_group_id\
                        and 'scale_group_id' not in list(vals.keys())
                    if not ignore:
                        is_continue = False
                        if not product.available_in_pos and\
                                'available_in_pos' not in vals:
                            is_continue = True
                        if product.available_in_pos and \
                                'available_in_pos' in vals and\
                                not vals.get('available_in_pos'):
                            is_continue = True

                        if is_continue:
                            defered[product.id] = 'unlink'
                            continue

                        if not product.scale_group_id:
                            # (the product is new on this group)
                            defered[product.id] = 'create'
                        else:
                            if vals.get('scale_group_id', False) and (
                                    vals.get('scale_group_id', False) !=
                                    product.scale_group_id):
                                # (the product has moved from a group to another)
                                # Remove from obsolete group
                                product_obj._send_to_scale_bizerba('unlink', product)
                                # Create in the new group
                                defered[product.id] = 'create'
                            elif product_obj._check_vals_scale_bizerba(vals, product):
                                # Data related to the scale
                                defered[product.id] = 'write'
                            elif vals.get('available_in_pos'):
                                defered[product.id] = 'create'
        ctx['bizerba_off'] = True
        res = super(ProductTemplate, self).write(vals)

        for product_id, action in defered.items():
            product = product_obj.browse(product_id)
            product_obj._send_to_scale_bizerba(action, product)
        return res
