# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    scale_logo_code = fields.Char(string="Scale Logo Code", readonly=True)

    @api.model
    def create(self, vals):
        vals['scale_logo_code'] = '1'
        if 'label_ids' in vals:
            label_ids_val = vals.get("label_ids", [])
            if label_ids_val and isinstance(label_ids_val, list) and \
                    len(label_ids_val[0]) == 3:
                label_ids = label_ids_val[0][2]
                labels = self.env['product.label'].browse(label_ids)
                vals['scale_logo_code'] = labels and \
                    labels[0].scale_logo_code or '1'

        res = super(ProductTemplate, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'label_ids' in vals:
            for product in self:
                current_logo_code = product.scale_logo_code
                res = super(ProductTemplate, product).write(vals)

                # Browse again to see check the value
                updated_prod = self.browse(product.id)
                new_logo_code = updated_prod.label_ids and \
                    updated_prod.label_ids[0].scale_logo_code or '1'

                # Only trigger the change if it is actually change
                if current_logo_code != new_logo_code:
                    res = super(ProductTemplate, updated_prod).write(
                        {'scale_logo_code': new_logo_code}
                    )
        else:
            return super(ProductTemplate, self).write(vals)
        return res
