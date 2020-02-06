# coding: utf-8
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Columns Section
    print_category_id = fields.Many2one(
        string='Print Category', comodel_name='product.print.category',
        default=lambda s: s._default_print_category_id())

    to_print = fields.Boolean(
        string='Pricetag to reprint', compute='_compute_to_print', store=True)

    # Default Section
    def _default_print_category_id(self):
        return self.env.user.company_id.print_category_id

    # Compute Section
    @api.multi
    @api.depends('product_variant_ids.to_print')
    def _compute_to_print(self):
        for template in self:
            template.to_print = any(
                p.to_print for p in template.product_variant_ids)

    # Overload Section
    @api.model
    def create(self, vals):
        if vals.get('print_category_id', False):
            vals['to_print'] = True
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        template_ids = []
        for template in self:
            if template.print_category_id:
                if len(list(
                        set(vals.keys()) &
                        set(template.print_category_id.field_ids.
                            mapped('name')))):
                    template_ids.append(template.id)
        templates = self.browse(template_ids)
        super(ProductTemplate, templates).write({'to_print': True})
        products = self.env['product.product'].search(
            [('product_tmpl_id', 'in', tuple(template_ids))])
        products.write({'to_print': True})
        return res
