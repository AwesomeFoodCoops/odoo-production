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

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Constant Values
    _TARGET_TYPE = [
        ('product_price_inv_eq', '€'),
        ('time', 'days'),
        ('weight_net', 'kg'),
    ]

    # Columns Section
    purchase_target = fields.Integer('Purchase Target')
    target_type = fields.Selection(
        _TARGET_TYPE, 'Target Type', required=True,
        default='product_price_inv_eq',
        help="""This defines the amount of products you want to"""
        """ purchase. \n"""
        """The system will compute a purchase order based on the stock"""
        """ you have and the average consumption of each product."""
        """* Target type '€': computed purchase order will cost"""
        """ at least the amount specified\n"""
        """* Target type 'days': computed purchase order will last at"""
        """ least the number of days specified (according to current"""
        """ average consumption)\n"""
        """* Target type 'kg': computed purchase order will weight"""
        """ at least the weight specified""")
