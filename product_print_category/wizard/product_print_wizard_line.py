# coding: utf-8
# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProductPrintWizardLine(models.TransientModel):
    _name = 'product.print.wizard.line'
    _rec_name = 'product_id'

    # Columns Section
    wizard_id = fields.Many2one(comodel_name='product.print.wizard')

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)

    print_category_id = fields.Many2one(
        comodel_name='product.print.category', string='Print Category',
        required=True, related='product_id.print_category_id')

    quantity = fields.Integer(string='Quantity', required=True, default=1)
