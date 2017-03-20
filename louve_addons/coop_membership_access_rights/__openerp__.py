# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2017-Today Akretion (https://www.akretion.com)
#    @author Julien WESTE
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

{
    'name': 'Coop Membership Access Rights',
    'version': '9.0.0.0',
    'category': 'Custom',
    'description': """
        For simpler rights management, create a new single partner view
        including all the views: the Bureau Des Membres view.
    """,
    'author':
    'Julien WESTE, Sylvain LE GAL (https://twitter.com/legalsylvain),',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'depends': [
        'barcodes_generate',
        'base',
        'coop_shift',
        'louve_membership',
    ],
    'data': [
        'security/res_group.xml',
        'security/ir_model_access.yml',
        'views/menu.xml',
        'views/res_partner_view.xml',
        'views/shift_view.xml',
    ],
}
