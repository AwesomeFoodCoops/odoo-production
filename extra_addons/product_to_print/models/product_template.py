# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    category_print_id = fields.Many2one(
        string='Print Category', comodel_name='product.category.print')

    @api.model
    def create(self, vals):
        if vals.get('category_print_id', False):
            vals['to_print'] = True
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        template_ids = []
        for template in self:
            if template.category_print_id:
                if len(list(
                        set(vals.keys()) &
                        set(template.category_print_id.field_ids.
                            mapped('name')))):
                    template_ids.append(template.id)
        templates = self.browse(template_ids)
        super(ProductTemplate, templates).write({'to_print': True})
        products = self.env['product.product'].search(
            [('product_tmpl_id', 'in', tuple(template_ids))])
        products.write({'to_print': True})
        return res
