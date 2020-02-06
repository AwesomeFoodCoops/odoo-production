# coding: utf-8
# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class ProductPrintWizard(models.TransientModel):
    _name = 'product.print.wizard'

    line_ids = fields.One2many(
        comodel_name='product.print.wizard.line', inverse_name='wizard_id',
        string='Lines', default=lambda s: s._default_line_ids())

    @api.model
    def _default_line_ids(self):
        lines_vals = []
        context = self.env.context
        product_obj = self.env['product.product']
        if context.get('active_model', False) == 'product.print.category':
            domain = [
                ('print_category_id.id', 'in', context.get('active_ids', [])),
            ]
            if not context.get('all_products', False):
                domain.append(('to_print', '=', True))
            products = product_obj.search(domain)

        elif context.get('active_model', False) == 'product.product':
            product_ids = context.get('active_ids', [])
            products = product_obj.browse(product_ids)
        elif context.get('active_model', False) == 'product.template':
            template_ids = context.get('active_ids', [])
            products = product_obj.search([
                ('product_tmpl_id', 'in', template_ids),
            ])
        else:
            return False

        # Initialize lines
        products_without = products.filtered(lambda x: not x.print_category_id)
        if products_without:
                raise UserError(_(
                    "The following products has not print category defined."
                    " Please define one before.\n %s") % (
                        '\n'.join([x.name for x in products_without])))
        for product in products:
                lines_vals.append((0, 0, {
                    'product_id': product.id,
                    'print_category_id': product.print_category_id.id,
                    'quantity': 1,
                }))
        return lines_vals

    # View Section
    @api.multi
    def print_report(self):
        self.ensure_one()
        data = self._prepare_data()
        return self.env['report'].get_action(
            self, 'product_print_category.report_pricetag', data=data)

    @api.multi
    def _prepare_data(self):
        return {
            'line_data': [x.id for x in self.line_ids],
        }

    @api.multi
    def _prepare_product_data(self):
        self.ensure_one()
        product_data = {}
        for line in self.line_ids:
            if line.product_id.id not in product_data:
                product_data[line.product_id.id] = line.quantity
            else:
                product_data[line.product_id.id] += line.quantity
        return product_data
