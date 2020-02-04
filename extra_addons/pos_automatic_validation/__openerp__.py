# -*- coding: utf-8 -*-
##############################################################################
#
#    POS Payment Validation module for Odoo
#    Copyright (C) 2017 Julius Network Solutions <contact@julius.fr>
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
    'name': 'POS Automatic Validation',
    'version': '9.0.0.1.0',
    'category': 'Point Of Sale',
    'summary': 'Manage Automatic Validation after complete '
    'payment in the POS front end',
    'author': "Julius Network Solutions",
    'contributors': ['Mathieu VATEL <mathieu@julius.fr>'],
    'license': 'AGPL-3',
    'depends': ['point_of_sale'],
    'data': [
             'views/account_journal_view.xml',
             'static/src/xml/templates.xml',
             ],
    'installable': True,
}
