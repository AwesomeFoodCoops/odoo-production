# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        allow_inactive_search_fields = ['barcode']
        allow_inactive_search_field_domain = filter(
            lambda arg: not isinstance(arg, basestring) and
                        arg[0] in allow_inactive_search_fields, args)
        if allow_inactive_search_field_domain:
            args.append('|')
            args.append(('active', '=', True))
            args.append(('active', '=', False))
        return super(ProductProduct, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        allow_inactive_search_fields = ['barcode']
        allow_inactive_search_field_domain = filter(
            lambda arg: not isinstance(arg, basestring) and
                        arg[0] in allow_inactive_search_fields, args)
        if allow_inactive_search_field_domain:
            args.append('|')
            args.append(('active', '=', True))
            args.append(('active', '=', False))
        return super(ProductTemplate, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count)
