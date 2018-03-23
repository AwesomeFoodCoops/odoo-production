# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author Julien Weste - La Louve 2016
#    Inspired by Smile (smile_export_sage_100)
#    and GRAP (account_export_ebp)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account Export',
    'version': '1.0',
    'depends': ['account', 'document'],
    "author": "Julien Weste",
    'description': """Provides generic functionalities to export account moves
    as csv files that will be imported in accounting softwares
    """,
    "summary": "Export account move lines for accounting software",
    "category": 'Accounting & Finance',
    "sequence": 10,
    "license": "AGPL-3",
    'images': [],
    'data': [
        'views/account_view.xml',
        'views/res_partner_view.xml',
        'views/export_view.xml',
        "security/account_export_security.xml",
        "security/ir.model.access.csv",
    ],
}
