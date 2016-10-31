# -*- coding: utf-8 -*-
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model


class product_scale_system_product_line(Model):
    _name = 'product.scale.system.product.line'
    _order = 'scale_system_id, sequence'

    _TYPE_SELECTION = [
        ('id', 'Product ID'),
        ('numeric', 'Numeric Field'),
        ('text', 'Char / Text Field'),
        ('external_text', 'External Text Field'),
        ('constant', 'Constant Value'),
        ('external_constant', 'External Constant Text Value'),
        ('many2one', 'ManyOne Field'),
        ('many2many', 'Many2Many Field'),
        ('product_image', 'Product Image'),
    ]

    # Column Section
    _columns = {
        'scale_system_id': fields.many2one(
            'product.scale.system', 'Scale System', required=True,
            ondelete='cascade', select=True),
        'company_id': fields.related(
            'scale_system_id', 'company_id', type='many2one', string='Company',
            relation='res.company', store=True),
        'code': fields.char(string='Bizerba Code', required=True),
        'name': fields.char(string='Name', required=True),
        'sequence': fields.integer(string='Sequence', required=True),
        'type': fields.selection(
            _TYPE_SELECTION, string='Type'),
        'field_id': fields.many2one(
            'ir.model.fields', string='Product Field', domain="["
            "('model', 'in', ['product.product', 'product.template'])]"),
        # TODO Improve. Set domain, depending on the other field
        'related_field_id': fields.many2one(
            'ir.model.fields', string='M2M / M2O Field', help="Used only"
            " for the x2x fields. Set here the field of the related model"
            " that you want to send to the scale. Let empty to send the ID."),
        'x2many_range': fields.integer(
            string='range of the x2Many Fields', help="Used if type is"
            " 'Many2Many Field', to mention the"
            " range of the field  to send. Begin by 0. (used for exemple"
            " for product logos)"),
        'constant_value': fields.char(
            string='Constant Value', help="Used if type is 'constant',"
            " to send allways the same value."),
        'multiline_length': fields.integer(
            string='Length for Multiline',
            help="Used if type is 'Text Field' or 'External Text Constant'"
            ", to indicate the max length of a line. Set 0 to avoid to split"
            " the value."),
        'multiline_separator': fields.char(
            string='Separator for Multiline', help="Used if type is"
            " 'Text Field' or 'External Text Constant', to indicate wich text"
            " will be used to mention break lines."),
        # TODO Improve. Set contrains.
        'suffix': fields.char(
            string='Suffix', help="Used if type is"
            " 'External Text Field', to indicate how to suffix the field.\n"
            " Make sure to have a uniq value by Scale System, and all with the"
            " same size.\n\n Used if type is Product Image to mention the end"
            " of the file. Exemple : '_01.jpg'."),
        'numeric_coefficient': fields.float(
            string='Numeric Coefficient', help="Used if type is"
            " 'Numeric Field', to mention with coefficient numeric"
            " field should be multiplyed."),
        'numeric_round': fields.float(
            string='Rounding Method', help="Used if type is"
            " 'Numeric Field', to mention how the value should be rounded.\n"
            " Do not Use 0, because it will truncate the value."),
        'delimiter': fields.char(
            string='Delimiter Char', help="Used to finish the column"),
    }

    _defaults = {
        'sequence': 10,
        'multiline_length': 0,
        'multiline_separator': '\n',
        'numeric_coefficient': 1,
        'numeric_round': 1,
        'delimiter': '#',
    }
