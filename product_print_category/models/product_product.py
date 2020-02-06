# coding: utf-8
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    print_category_id = fields.Many2one(
        string='Print Category', related='product_tmpl_id.print_category_id')

    to_print = fields.Boolean(string='To Print')

    @api.model
    def create(self, vals):
        if vals.get('print_category_id', False):
            vals['to_print'] = True
        return super(ProductProduct, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        product_ids = []
        for product in self:
            if product.print_category_id:
                if len(list(
                        set(vals.keys()) &
                        set(product.print_category_id.field_ids.
                            mapped('name')))):
                    product_ids.append(product.id)
        products = self.browse(product_ids)
        super(ProductProduct, products).write({'to_print': True})
        return res
