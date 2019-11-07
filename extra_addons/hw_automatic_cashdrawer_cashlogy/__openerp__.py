# -*- encoding: utf-8 -*-
##############################################################################
#
#    Hardware Telium Payment Terminal module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Hardware Cashlogy Automatic Cashdrawer',
    'version': '8.0.0.1.0',
    'category': 'Hardware Drivers',
    'license': 'AGPL-3',
    'summary': 'Adds support for Cashlogy Automatic Cashdrawer',
    'description': """
Hardware Cashlogy Automatic Cashdrawer
======================================

This module adds support for automatic cashdrawer from the Cashlogy/AzkoyenGroup. This module is designed to
be installed on the *POSbox* (i.e. the proxy on which the USB devices
are connected) and not on the main Odoo server. On the main Odoo server,
you should install the module *pos_automatic_cashdrawer*.

For now, it depends on the CashlogyConnector.

This module has been written by Aurélien DUMAINE <aurelien.dumaine@free.fr>
    """,
    'author': "Aurélien DUMAINE",
    'website': 'http://dumaine.me',
    'depends': ['hw_proxy'],
    'external_dependencies': {
        'python': ['serial'],
    },
    'data': [],
    'installable': True,
}
