# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('farming_method', 'other_information')
    @api.multi
    def _compute_pricetag_louveinfos(self):
        for pt in self:
            tmp = ''
            if pt.other_information:
                tmp = pt.other_information
            if pt.farming_method:
                tmp = pt.farming_method + \
                    (' - ' + tmp if tmp else '')
            pt.pricetag_louveinfos = tmp

    @api.depends(
        'rack_instruction', 'rack_location', 'rack_number_of_packages',
        'default_seller_id')
    @api.multi
    def _compute_pricetag_rackinfos(self):
        for pt in self:
            tmp = ''
            if pt.rack_instruction:
                tmp = pt.rack_instruction
            if pt.rack_location:
                tmp = pt.rack_location + \
                    (' - ' + tmp if tmp else '')
            if pt.rack_number_of_packages:
                tmp = pt.rack_number_of_packages + \
                    (' - ' + tmp if tmp else '')
            if pt.default_seller_id.package_qty:
                tmp = str(pt.default_seller_id.package_qty) + \
                    (' - ' + tmp if tmp else '')
            pt.pricetag_rackinfos = tmp

    def _default_category_print_id(self):
        category_obj = self.env['product.category.print']
        category_ids = category_obj.search(
            [('is_default', '=', True)], limit=1)
        return category_ids and category_ids[0] or category_ids

    # Column Section
    rack_instruction = fields.Char(
        "Rack Instruction", help="""For example, the number of packages that
        should be stored on the rack""")
    rack_location = fields.Char(
        "Rack Location", help="""The name or place of the rack""")
    rack_number_of_packages = fields.Char(
        "Number of packages on the rack")
    farming_method = fields.Char(
        "Farming Method", help="""Organic Label""")
    other_information = fields.Char("Other Information")
    pricetag_rackinfos = fields.Char(
        compute=_compute_pricetag_rackinfos, string='La Louve rack fields')
    pricetag_louveinfos = fields.Char(
        compute=_compute_pricetag_louveinfos, string='La Louve custom fields')
    category_print_id = fields.Many2one(
        comodel_name='product.category.print', string='Print Category',
        default=lambda self: self._default_category_print_id())
