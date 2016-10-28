# -*- coding: utf-8 -*-
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model


class product_scale_system(Model):
    _name = 'product.scale.system'

    # Constant section
    _ENCODING_SELECTION = [
        ('iso-8859-1', 'Latin 1 (iso-8859-1)'),
    ]

    # Compute Section
    def _get_field_ids(
            self, cr, uid, ids, field_names, arg=None, context=None):
        res = {}
        for id in ids:
            res.setdefault(id, [])
        for system in self.browse(cr, uid, ids, context=context):
            for product_line in system.product_line_ids:
                if product_line.field_id:
                    res[system.id].append(product_line.field_id.id)
        return res

    # Column Section
    _columns = {
        'name': fields.char(
            string='Name', required=True),
        'company_id': fields.many2one(
            'res.company', string='Company', select=True),
        'active': fields.boolean(
            string='Active'),
        'ftp_url': fields.char(
            string='FTP Server URL'),
        'ftp_login': fields.char(
            string='FTP Login'),
        'ftp_password': fields.char(
            string='FTP Password'),
        'encoding': fields.selection(
            _ENCODING_SELECTION, string='Encoding', required=True),
        'csv_relative_path': fields.char(
            string='Relative Path for CSV', required=True),
        'product_image_relative_path': fields.char(
            string='Relative Path for Product Images', required=True),
        'product_text_file_pattern': fields.char(
            string='Product Text File Pattern', required=True, help="Pattern"
            " of the Product file. Use % to include dated information.\n"
            " Ref: https://docs.python.org/2/library/time.html#time.strftime"),
        'external_text_file_pattern': fields.char(
            string='External Text File Pattern', required=True, help="Pattern"
            " of the External Text file. Use % to include dated information.\n"
            " Ref: https://docs.python.org/2/library/time.html#time.strftime"),
        'product_line_ids': fields.one2many(
            'product.scale.system.product.line', 'scale_system_id',
            'Product Lines'),
        'field_ids': fields.function(
            _get_field_ids, type='one2many', string='Fields',
            relation='ir.model.fields'),
    }

    _defaults = {
        'active': True,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company').
        _company_default_get(cr, uid, 'product.template', context=c),
        'encoding': 'iso-8859-1',
        'ftp_url': 'xxx.xxx.xxx.xxx',
        'csv_relative_path': '/',
        'product_image_relative_path': '/',
        'product_text_file_pattern': 'product.csv',
        'external_text_file_pattern': 'external_text.csv',
    }
